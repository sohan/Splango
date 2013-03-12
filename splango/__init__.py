import logging

from django.utils.encoding import smart_unicode
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from .models import Subject, Experiment, Enrollment, GoalRecord
from .utils import is_first_visit, replace_insensitive


logger = logging.getLogger(__name__)

SPLANGO_STATE = "SPLANGO_STATE"
SPLANGO_SUBJECT = "SPLANGO_SUBJECT"
SPLANGO_QUEUED_UPDATES = "SPLANGO_QUEUED_UPDATES"
S_UNKNOWN = "UNKNOWN"
S_HUMAN = "HUMAN"

# borrowed from debug_toolbar
_HTML_TYPES = ('text/html', 'application/xhtml+xml')


class RequestExperimentManager:

    def __init__(self, request):
        #logger.debug("REM init")
        self.request = request
        self.user_at_init = request.user
        self.queued_actions = []

        if self.request.session.get(SPLANGO_STATE) is None:
            self.request.session[SPLANGO_STATE] = S_UNKNOWN

            if is_first_visit(self.request):
                logger.info("First visit!")

                first_visit_goal_name = getattr(
                    settings, "SPLANGO_FIRST_VISIT_GOAL", None)

                # TODO: shouldn't this be ``if first_visit_goal_name is None``?
                if first_visit_goal_name:
                    self.log_goal(first_visit_goal_name)

    def enqueue(self, action, params):
        self.queued_actions.append((action, params))

    def process_from_queue(self, action, params):
        logger.info("dequeued: %s (%s)" % (str(action), repr(params)))

        if action == "enroll":
            exp = Experiment.objects.get(name=params["exp_name"])
            variant = params["variant"]
            exp.get_or_create_enrollment(self.get_subject(), variant)

        elif action == "log_goal":
            goal_record = GoalRecord.record(self.get_subject(),
                                            params["goal_name"],
                                            params["request_info"],
                                            extra=params.get("extra"))
            logger.info("goal! %s" % str(goal_record))

        else:
            raise RuntimeError("Unknown queue action '%s'." % action)

    def render_js(self):
        logger.info("render_js")

        pre_js = ""
        post_js = ""

        if settings.DEBUG:
            pre_js = "try { "
            post_js = (' } catch(e) { alert("DEBUG notice: Splango encountered '
                       'a javascript error when attempting to confirm this '
                       'user as a human. Is jQuery loaded?\\n\\nYou may notice '
                       'inconsistent experiment enrollments until this is '
                       'fixed.\\n\\nDetails:\\n"+e.toString()); }')

        try:
            url = reverse("splango_confirm_human")
        except NoReverseMatch:
            url = "/splango/confirm_human/"

        return ("<script type='text/javascript'>"
                "%sjQuery.get(\"%s\");"
                "%s</script>" % (pre_js, url, post_js))

    def confirm_human(self, reqdata=None):
        logger.info("Human confirmed!")
        self.request.session[SPLANGO_STATE] = S_HUMAN

        for (action, params) in self.request.session.get(
                SPLANGO_QUEUED_UPDATES, []):
            self.process_from_queue(action, params)

    def finish(self, response):
        """Decide what to do if subject is human or not."""

        current_state = self.request.session.get(SPLANGO_STATE, S_UNKNOWN)

        #logger.info("finished... state=%s" % current_state)

        current_user = self.request.user

        if self.user_at_init != current_user:
            logger.info("user status changed over request: %s --> %s"
                        % (str(self.user_at_init), str(current_user)))

            if not(current_user.is_authenticated()):
                # User logged out. It's a new session, nothing special.
                pass
            else:
                # User has just logged in (or registered).
                # We'll merge the session's current Subject with
                # an existing Subject for this user, if exists,
                # or simply set the subject.registered_as field.

                self.request.session[SPLANGO_STATE] = S_HUMAN
                # logging in counts as being proved a human

                old_subject = self.request.session.get(SPLANGO_SUBJECT)

                try:
                    existing_subject = Subject.objects.get(
                        registered_as=current_user)
                    # there is an existing registered subject!
                    if old_subject and old_subject.id != existing_subject.id:
                        # merge old subject's activity into new
                        old_subject.merge_into(existing_subject)

                    # whether we had an old_subject or not, we must
                    # set session to use our existing_subject
                    self.request.session[SPLANGO_SUBJECT] = existing_subject

                except Subject.DoesNotExist:
                    # promote current subject to registered!
                    subject = self.get_subject()
                    subject.registered_as = current_user
                    subject.save()

        if current_state == S_HUMAN:
            # run anything in my queue
            for (action, params) in self.queued_actions:
                self.process_from_queue(action, params)
            self.queued_actions = []
        else:
            # shove queue into session
            (
                self.request.session
                .setdefault(SPLANGO_QUEUED_UPDATES, [])
                .extend(self.queued_actions))
            self.queued_actions = []

            # and include JS if suitable for this response.
            if response['Content-Type'].split(';')[0] in _HTML_TYPES:
                response.content = replace_insensitive(
                    smart_unicode(response.content), u'</body>',
                    smart_unicode(self.render_js() + u'</body>'))

        return response

    def get_subject(self):
        # TODO: what if session[SPLANGO_STATE] throws KeyError?
        assert(self.request.session[SPLANGO_STATE] == S_HUMAN,
               ("Hey, you can't call get_subject until you know the subject "
                "is a human!"))

        subject = self.request.session.get(SPLANGO_SUBJECT)
        if not subject:  # TODO: shouldn't this be ``if subject is None``?
            subject = Subject()
            self.request.session[SPLANGO_SUBJECT] = subject
            subject.save()
            logger.info("created subject: %s" % str(subject))

        return subject

    def declare_and_enroll(self, exp_name, variants):
        exp = Experiment.declare(exp_name, variants)

        # TODO: what if session[SPLANGO_STATE] throws KeyError?
        if self.request.session[SPLANGO_STATE] != S_HUMAN:
            logger.info("choosing new random variant for non-human")
            variant = exp.get_random_variant()
            self.enqueue("enroll", {"exp_name": exp.name, "variant": variant})

        else:
            subject = self.get_subject()
            subject_variant = exp.get_or_create_enrollment(subject)
            variant = subject_variant.variant
            logger.info("got variant %s for subject %s" %
                        (str(variant), str(subject)))

        return variant

    def log_goal(self, goal_name, extra=None):
        request_info = GoalRecord.extract_request_info(self.request)

        self.enqueue("log_goal", {
            "goal_name": goal_name,
            "request_info": request_info,
            "extra": extra
        })
