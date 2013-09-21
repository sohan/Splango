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

    def __init__(self, exp_name, variants_str):
        """Save the experiment and variants names, splitting ``variants_str``.

        :attr:`variants` is a list of strings, the name of each variant

        :param exp_name: experiment name
        :param variants_str: variants names concatenated by ``","`` e.g.
          ``"red,blue,green"``

        """
        self.exp_name_var = django.template.Variable(exp_name)
        self.variants_str_var = django.template.Variable(variants_str)

    def render(self, context):
        """Declare the experiment and enroll a variant. Render nothing.

        :param context: template context
        :type context: :class:`django.template.context.Context`
        :return: empty string
        :rtype: basestring
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

        #resolve template vars, throws an error
        exp_name = self.exp_name_var.resolve(context)
        variants = self.variants_str_var.resolve(context)
        variants = [v.strip() for v in variants.split(u',')]


        variant = exp_manager.declare_and_enroll(exp_name, variants)
        context[CTX_PREFIX + exp_name] = variant
        msg = ("Completed ExperimentNode.render"
               "\nexp name: %s, exp variants: %s, enrolled variant: %s" %
               (exp_name, variants, variant))
        logger.debug(msg)

        return ""


class HypNode(django.template.Node):

    """Template node for a ``{% hyp %}`` template tag.

    This :meth:`render` method of this class either returns an empty string
    or the inner nodes rendered.

    """

    def __init__(self, exp_name, exp_variant, node_list):
        self.exp_name_var = django.template.Variable(exp_name)
        self.exp_variant_var = django.template.Variable(exp_variant)

        self.node_list = node_list

    def render(self, context):
        """Render the node list if :attr:`exp_variant` is the enrolled variant.

        :param context: template context
        :type context: :class:`django.template.context.Context`
        :return: :attr:`node_list` rendered or an empty string
        :rtype: basestring
        :raises: :class:`django.template.TemplateSyntaxError` if the experiment
          named :attr:`exp_name` has not been declared yet

        """

        #resolve template vars, throws an error
        exp_name = self.exp_name_var.resolve(context)
        exp_variant = self.exp_variant_var.resolve(context)

        msg = ("Rendering HypNode. exp name: %s, exp variant: %s" %
               (exp_name, exp_variant))
        logger.debug(msg)

        enrolled_variant_name = self._get_enrolled_variant_name(context)
        logger.debug("enrolled variant name %s" % enrolled_variant_name)

        if exp_variant == enrolled_variant_name:
            # render the contents within {% hyp %} and {% endhyp %}
            return self.node_list.render(context)
        else:
            # render nothing and the contents are discarded
            logger.debug("HypNode(%s, %s) not rendered" %
                         (exp_name, exp_variant))
            return ""

    def _get_enrolled_variant_name(self, context):
        exp_name = self.exp_name_var.resolve(context)
        ctx_var = CTX_PREFIX + exp_name
        if ctx_var not in context:
            logger.error(UNDECLARED_EXPERIMENT_WARNING)
            raise TemplateSyntaxError(UNDECLARED_EXPERIMENT_WARNING)
        return context[ctx_var].name

@register.simple_tag(takes_context=True)
def enrolled_variant_name(context, exp_name):
    '''
    Returns the enrolled variant's name
    '''
    ctx_var = CTX_PREFIX + exp_name
    if ctx_var not in context:
        logger.error(UNDECLARED_EXPERIMENT_WARNING)
        raise TemplateSyntaxError(UNDECLARED_EXPERIMENT_WARNING)
    return context[ctx_var].name

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
        tag_name, exp_name, variants_label, variants_str = token.split_contents()
    except ValueError:
        tag_name = token.contents.split()[0]
        msg = ('%r tag requires exactly three arguments, e.g. {%% experiment '
               '"signuptext" variants "control,free,trial" %%}' % tag_name)
        logger.error(msg)
        raise TemplateSyntaxError(msg)

    return ExperimentNode(exp_name, variants_str)


@register.tag
def hyp(parser, token):
    """Return a :class:`HypNode` according to the contents of ``token``.

    Example::
        {% with exp_name="home_signup" variant_name="blue" %}
        {% hyp exp_name variant_name %}

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

    # parse until "endhyp" and then remove that token from parser
    node_list = parser.parse(("endhyp",))
    parser.next_token()

    return HypNode(exp_name, exp_variant, node_list)


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
