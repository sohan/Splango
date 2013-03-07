import logging
import random

from django.db import models
from django.contrib.auth.models import User


logger = logging.getLogger(__name__)

_NAME_LENGTH = 30


class Goal(models.Model):

    """An experiment goal, that is what we are waiting to happen."""

    name = models.CharField(max_length=_NAME_LENGTH, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class Subject(models.Model):

    """An experimental subject, possibly also a registered user (at creation
    or later on."""

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    registered_as = models.ForeignKey(User, null=True, editable=False,
                                      unique=True)
    goals = models.ManyToManyField(Goal, through='GoalRecord')

    def __unicode__(self):
        if self.registered_as:
            prefix = "registered"
        else:
            prefix = "anonymous"

        return u"%s subject #%d" % (prefix, self.id)

    def merge_into(self, other_subject):
        """Move the enrollments and goal records associated with this subject
        into ``other_subject``, preserving ``other_subject``'s
        enrollments in case of conflict.

        """
        other_goals = dict(((g.name, 1) for g in other_subject.goals.all()))

        for goal_record in self.goalrecord_set.all().select_related("goal"):
            if goal_record.goal.name not in other_goals:
                goal_record.subject = other_subject
                goal_record.save()
            else:
                goal_record.delete()

        other_exps = dict(((e.experiment_id, 1)
                           for e in other_subject.enrollment_set.all()))

        for e in self.enrollment_set.all():
            if e.experiment_id not in other_exps:
                e.subject = other_subject
                e.save()
            else:
                e.delete()

        self.delete()


class GoalRecord(models.Model):

    """Associate the goal reached by a subject with that subject."""

    goal = models.ForeignKey(Goal)
    subject = models.ForeignKey(Subject)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    req_HTTP_REFERER = models.CharField(max_length=255, blank=True)
    req_REMOTE_ADDR = models.IPAddressField(blank=True)
    req_path = models.CharField(max_length=255, blank=True)

    extra = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = (('subject', 'goal'),)
        # never record the same goal twice for a given subject

    @staticmethod
    def extract_request_info(request):
        return dict(
            req_HTTP_REFERER=request.META.get("HTTP_REFERER", "")[:255],
            req_REMOTE_ADDR=request.META["REMOTE_ADDR"],
            req_path=request.path[:255])

    @classmethod
    def record(cls, subject, goal_name, request_info, extra=None):
        logger.warn("goal_record %r" %
                    [subject, goal_name, request_info, extra])
        goal, created = Goal.objects.get_or_create(name=goal_name)
        goal_record, created = cls.objects.get_or_create(
            subject=subject, goal=goal, defaults=request_info)

        if not created and not goal_record.extra and extra:
            # add my extra info to the existing goal record
            goal_record.extra = extra
            goal_record.save()

        return goal_record

    @classmethod
    def record_user_goal(cls, user, goal_name):
        subject, created = Subject.objects.get_or_create(registered_as=user)
        cls.record(subject, goal_name, {})

    def __unicode__(self):
        return u"%s by subject #%d" % (self.goal, self.subject_id)


class Enrollment(models.Model):

    """Identifies which variant a subject is assigned to in a given
    experiment."""

    subject = models.ForeignKey('splango.Subject', editable=False)
    experiment = models.ForeignKey('splango.Experiment', editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    variant = models.ForeignKey('splango.Variant')

    class Meta:
        unique_together = (('subject', 'experiment'),)

    def __unicode__(self):
        return (u"experiment '%s' subject #%d -- variant %s" %
                (self.experiment.name, self.subject_id, self.variant))


class Experiment(models.Model):

    """A named experiment."""

    name = models.CharField(max_length=_NAME_LENGTH, primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    subjects = models.ManyToManyField(Subject, through=Enrollment)

    def __unicode__(self):
        return self.name

    # def set_variants(self, variant_list):
    #     self.variants = "\n".join(variant_list)

    def get_variants(self):
        return self.variants.all()

    def get_random_variant(self):
        return random.choice(self.get_variants())

    def variants_commasep(self):
        variants = self.get_variants()
        variants_names = [v.name for v in variants]
        return ','.join(variants_names)

    def get_variant_for(self, subject):
        enrollment, created = Enrollment.objects.get_or_create(
            subject=subject,
            experiment=self,
            defaults={"variant": self.get_random_variant(), })
        return enrollment

    def enroll_subject_as_variant(self, subject, variant):
        enrollment, created = Enrollment.objects.get_or_create(
            subject=subject,
            experiment=self,
            defaults={"variant": variant, })
        return enrollment

    @classmethod
    def declare(cls, name, variants_names):
        """create or update an experiment and its variants (variant names
        given).

        """
        obj, created = cls.objects.get_or_create(name=name)

        for v in variants_names:
            Variant.objects.get_or_create(name=v, experiment=obj)
        return obj


class ExperimentReport(models.Model):

    """A report on the results of an experiment."""

    experiment = models.ForeignKey(Experiment)
    title = models.CharField(max_length=100, blank=True)
    funnel = models.TextField(
        help_text="List the goals, in order and one per line, that "
                  "constitute this report's funnel.")

    def __unicode__(self):
        return u"%s - %s" % (self.title, self.experiment.name)

    def get_funnel_goals(self):
        return [x.strip() for x in self.funnel.split("\n") if x]

    def generate(self):
        """Generate the report for experiment.

        Generate the report of a experiment goals and variants.

        Associate each variant with a goal, and associate the variant
        count too.

        :returns: A dict with goals, variants and variants counts associated
        to each goal

        """
        result = []
        exp = self.experiment
        variants = self.experiment.get_variants()
        goals = self.get_funnel_goals()

        # count initial participation
        variant_counts = []

        for v in variants:
            # variant_counts.append(exp.subjectvariant_set.filter(variant=v).\
            #     aggregate(ct=Count("variant")).get("ct",0))
            val = Enrollment.objects.filter(experiment=exp, variant=v).count()
            variant_counts.append(dict(
                val=val,
                variant_name=v,
                pct=None,
                pct_cumulative=1,
                pct_cumulative_round=100))

        result.append({"goal": None,
                       "variant_names": variants,
                       "variant_counts": variant_counts})

        for previ, goal in enumerate(goals):
            try:
                goal = Goal.objects.get(name=goal)
            except Goal.DoesNotExist:
                logger.warn("No such goal <<%s>>." % goal)
                goal = None

            variant_counts = []

            for vi, v in enumerate(variants):
                if goal:
                    vcount = Enrollment.objects.filter(
                        experiment=exp, variant=v, subject__goals=goal).count()
                    prev_count = result[previ]["variant_counts"][vi]["val"]

                    if prev_count == 0:
                        pct = 0
                    else:
                        pct = float(vcount) / float(prev_count)

                else:
                    vcount = 0
                    pct = 0

                pct_cumulative = \
                    pct * result[previ]["variant_counts"][vi]["pct_cumulative"]

                variant_counts.append(dict(
                    val=vcount,
                    variant_name=variants[vi],
                    pct=pct,
                    pct_round=("%0.2f" % (100 * pct)),
                    pct_cumulative=pct_cumulative,
                    pct_cumulative_round=("%0.2f" % (100 * pct_cumulative)), ))

            result.append({"goal": goal, "variant_counts": variant_counts})

        return result


class Variant(models.Model):

    """An Experiment Variant, with optional weight"""

    experiment = models.ForeignKey('splango.Experiment',
                                   related_name="variants")

    name = models.CharField(max_length=100, blank=True)
    weight = models.IntegerField(null=True, blank=True,
                                 help_text="The priority of the variant")

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.experiment)

