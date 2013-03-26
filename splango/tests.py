from django.test import TestCase

from . import models


###############################################################################
# Model factories
###############################################################################


def create_goal(**kwargs):
    defaults = {'name': 'My goal', }
    defaults.update(kwargs)

    return models.Goal.objects.create(**defaults)


def create_subject(**kwargs):
    defaults = {}
    defaults.update(kwargs)

    return models.Subject.objects.create(**defaults)


def create_goal_record(**kwargs):
    defaults = {}
    defaults.update(kwargs)

    if 'goal' not in defaults:
        defaults['goal'] = create_goal()
    if 'subject' not in defaults:
        defaults['subject'] = create_subject()

    return models.GoalRecord.objects.create(**defaults)


def create_enrollment(**kwargs):
    defaults = {}
    defaults.update(kwargs)

    if 'subject' not in defaults:
        defaults['subject'] = create_subject()
    if 'experiment' not in defaults:
        defaults['experiment'] = create_experiment()
    if 'variant' not in defaults:
        defaults['variant'] = create_variant()

    return models.Enrollment.objects.create(**defaults)


def create_experiment(**kwargs):
    defaults = {'name': 'My experiment', }
    defaults.update(kwargs)

    return models.Experiment.objects.create(**defaults)


def create_experiment_report(**kwargs):
    defaults = {'title': 'My experiment report', }
    defaults.update(kwargs)

    if 'experiment' not in defaults:
        defaults['experiment'] = create_experiment()

    return models.ExperimentReport.objects.create(**defaults)


def create_variant(**kwargs):
    defaults = {'name': 'A variant', }
    defaults.update(kwargs)

    if 'experiment' not in defaults:
        defaults['experiment'] = create_experiment()

    return models.Variant.objects.create(**defaults)


class GoalRecord(TestCase):

    pass
