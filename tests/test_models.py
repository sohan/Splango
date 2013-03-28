from django.db.utils import IntegrityError
from django.test import TestCase

from splango.models import Experiment, Subject, GoalRecord
from splango.tests import (
    create_goal, create_goal_record, create_subject, create_enrollment,
    create_experiment, create_experiment_report, create_variant)


class GoalTest(TestCase):

    pass


class SubjectTest(TestCase):

    pass


class GoalRecordTest(TestCase):

    def test_unique_together(self):
        goal = create_goal()
        subject = create_subject()
        create_goal_record(goal=goal, subject=subject)

        self.assertRaises(
            IntegrityError, create_goal_record, goal=goal, subject=subject)


class EnrollmentTest(TestCase):

    def test_unique_together(self):
        var = create_variant()
        subject = create_subject()
        create_enrollment(variant=var, subject=subject)

        self.assertRaises(
            IntegrityError, create_enrollment, variant=var, subject=subject)

    def test_unicode(self):
        enrollment = create_enrollment()
        self.assertEqual(
            "experiment 'My experiment' subject #1 -- variant A variant",
            enrollment.__unicode__())

    def test_experiment(self):
        enrollment = create_enrollment()
        self.assertIsInstance(enrollment.experiment, Experiment)


class ExperimentTest(TestCase):

    pass


class ExperimentReportTest(TestCase):

    pass


class VariantTest(TestCase):

    pass
