# -*- coding: utf-8 -*-
from splango.models import (Experiment, Variant, Subject)


def create_experiment(**kwargs):
    defaults = {
        'name': u'Experiment 1'
    }
    defaults.update(kwargs)
    return Experiment.objects.create(**defaults)


def create_subject(**kwargs):
    defaults = {
        #'user': None
    }
    defaults.update(kwargs)
    return Subject.objects.create(**defaults)


def create_variant(**kwargs):
    defaults = {
        'name': u'Variant 1'
    }
    defaults.update(kwargs)

    if 'experiment' not in defaults:
        defaults['experiment'] = create_experiment()

    return Variant.objects.create(**defaults)

