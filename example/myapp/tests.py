# -*- coding: utf-8 -*-
from unittest import TestCase
from mock import MagicMock
from splango import RequestExperimentManager
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


class InitTest(TestCase):
    """Tests for functions in splango.__init__
    """
    fixtures = ['admin_user.json']

    def setUp(self):
        self.variant_names = []
        self.experiment = create_experiment()
        self.variant1 = create_variant(name=u"variant 1",
                                       experiment=self.experiment)
        self.variant_names.append(self.variant1.name)
        self.variant2 = create_variant(name=u"variant 2",
                                       experiment=self.experiment)
        self.variant_names.append(self.variant2.name)

    def test_declare_and_enroll(self):
        """Test splango.RequestExperimentManager.declare_and_enroll()."""

        # RequestExperimentManager needs a request as a param.
        # Lets do a mock for the request.
        request = MagicMock()

        # Lets instanciate RequestExperimentManager now.
        exp_man = RequestExperimentManager(request)

        # It is needed a subject, because ``exp_man`` will call
        # ``get_subject()`` method. So we mock that method in order to have
        # the right returned value.
        subject_ = create_subject()
        exp_man.get_subject = MagicMock(name="Subject")
        exp_man.get_subject.return_value = subject_

        # Verify that ``get_subject()`` actually gets a `Subject` instance.
        mocked_subject = exp_man.get_subject()
        self.assertIsInstance(mocked_subject, Subject)

        # Now, call ``declare_and_enroll()`` and assert if the returned value
        # is a `Variant` instance.
        variant = exp_man.declare_and_enroll(self.experiment.name,
                                             self.variant_names, )
        self.assertIsInstance(variant, Variant)