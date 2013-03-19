import logging

import django.template
from django.template import TemplateSyntaxError


logger = logging.getLogger(__name__)
register = django.template.Library()

CTX_PREFIX = "__splango__experiment__"


UNDECLARED_EXPERIMENT_WARNING = (
    "Experiment has not yet been declared. Please declare it "
    "and supply variant names using an experiment tag before "
    "using hyp tags.")
REQUEST_CONTEXT_PROCESSOR_WARNING = (
    "Use of splangotags requires the request context processor. "
    "Please add django.core.context_processors.request to your "
    "settings.TEMPLATE_CONTEXT_PROCESSORS.")
SPLANGO_MIDDLEWARE_WARNING = (
    "Use of splangotags requires the splango middleware. Please "
    "add splango.middleware.ExperimentsMiddleware to your "
    "settings.MIDDLEWARE_CLASSES.")


class ExperimentNode(django.template.Node):

    """Template node for the {% experiment ... %} template tag.

    This

    :meth:`render` returns an empty string (thus
    ``{% experiment "..." variants "...,...,..." %}`` renders nothing) but
    it must be called so that the experiment is recorded appropriately.

    """

    def __init__(self, exp_name, variants):
        self.exp_name = exp_name
        self.variants = variants

    def render(self, context):
        """Declare the experiment and enroll a variant. Render nothing.

        :param context:
        :return: empty string
        :raises: :class:`django.template.TemplateSyntaxError` if ``'request'``
          is not in ``context``, or if the former does not have an experiments
          manager.

        """
        if "request" not in context:
            logger.error(REQUEST_CONTEXT_PROCESSOR_WARNING)
            raise TemplateSyntaxError(REQUEST_CONTEXT_PROCESSOR_WARNING)

        request = context["request"]
        exp_manager = request.experiments_manager
        if not exp_manager:
            logger.error(SPLANGO_MIDDLEWARE_WARNING)
            raise TemplateSyntaxError(SPLANGO_MIDDLEWARE_WARNING)

        exp_variant = exp_manager.declare_and_enroll(self.exp_name,
                                                     self.variants)
        context[CTX_PREFIX + self.exp_name] = exp_variant

        return ""  # "exp: %s - you are %s" % (self.exp_name, exp_variant)


class HypNode(django.template.Node):

    def __init__(self, exp_name, exp_variant, node_list):
        self.exp_name = exp_name
        self.exp_variant = exp_variant
        self.node_list = node_list

#         print ' ++ instantiated HypNode (%s, %s)' % (self.exp_name,
#                                                      self.exp_variant)

    def render(self, context):
#         print ' == rendering HypNode (%s, %s)' % (self.exp_name,
#                                                   self.exp_variant)

        ctx_var = CTX_PREFIX + self.exp_name

        if ctx_var not in context:
            logger.error(UNDECLARED_EXPERIMENT_WARNING)
            raise TemplateSyntaxError(UNDECLARED_EXPERIMENT_WARNING)

        if self.exp_variant == context[ctx_var].name:
            return self.node_list.render(context)
        else:
            return ""

        # TODO: cleanup these old returns, which can't be reached
        # return "[%s==%s]"%(self.exp_variant, context[ctx_var])+self.node_list.render(context)+"[/%s]"%self.exp_variant
        # 
        # return "HypNode: exp_name=%s, exp_variant=%s" % (self.exp_name,
        #                                                  self.exp_variant)


@register.tag
def experiment(parser, token):
    """Return a :class:`ExperimentNode` according to the contents of ``token``.

    Example::
        {% experiment "signup_button" variants "red,blue" %}

    :param parser: template parser object, not used
    :param token: tag contents i.e. between ``{% `` and `` %}``
    :type token: :class:`django.template.base.Token`
    :return: experiment node
    :rtype: :class:`ExperimentNode`
    :raises: :class:`django.template.TemplateSyntaxError` if tag arguments
      in ``token`` are different than three

    """
    try:
        tag_name, exp_name, variants_label, variant_str = token.split_contents()
    except ValueError:
        tag_name = token.contents.split()[0]
        msg = ('%r tag requires exactly three arguments, e.g. {%% experiment '
               '"signuptext" variants "control,free,trial" %%}' % tag_name)
        logger.error(msg)
        raise TemplateSyntaxError(msg)

    clean_exp_name = exp_name.strip("\"'")
    clean_variant_str = variant_str.strip("\"'")
    return ExperimentNode(clean_exp_name, clean_variant_str)


@register.tag
def hyp(parser, token):
    """Return a :class:`HypNode` according to the contents of ``token``.

    Example::
        {% hyp "signup_button" "blue" %}

    :param parser: template parser object
    :type parser: :class:`django.template.base.Parser`
    :param token: tag contents i.e. between ``{% `` and `` %}``
    :type token: :class:`django.template.base.Token`
    :return: experiment node
    :rtype: :class:`ExperimentNode`
    :raises: :class:`django.template.TemplateSyntaxError` if tag arguments
      in ``token`` are different than two

    """
    try:
        tag_name, exp_name, exp_variant = token.split_contents()
    except ValueError:
        tag_name = token.contents.split()[0]
        msg = "%r tag requires exactly two arguments" % tag_name
        logger.error(msg)
        raise TemplateSyntaxError(msg)

#     print "*** hyp looking for next tag"
    #print "parser.tokens = %r" % [ t.contents for t in parser.tokens ]

    node_list = parser.parse(("endhyp",))
    token = parser.next_token()

#     print " * hyp FOUND TOKEN %s" % token.contents
    parser.delete_first_token()
    #print "parser.tokens = %r" % [ t.contents for t in parser.tokens ]

    clean_exp_name = exp_name.strip("\"'")
    clean_variant_name = exp_variant.strip("\"'")
    return HypNode(clean_exp_name, clean_variant_name, node_list)


# I couldn't make this work well. Probably needs much more thought to work like
# a switch statement. See:
# http://djangosnippets.org/snippets/967/
#
# @register.tag
# def elsehyp(parser, token):
#     try:
#         tag_name, exp_variant = token.split_contents()
#     except ValueError:
#         raise TemplateSyntaxError(
#             "%r tag requires exactly one argument" % token.contents.split()[0]

#     #import pdb;pdb.set_trace()

#     print "*** elsehyp looking for next tag"
#     #print "parser.tokens = %r" % [ t.contents for t in parser.tokens ]

#     node_list = parser.parse(("elsehyp","endhyp"))

#     return HypNode(None, exp_variant, node_list)
