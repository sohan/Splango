from django.db.utils import IntegrityError
from django.test import TestCase

from splango.tests import (
    create_goal, create_goal_record, create_subject, create_enrollment,
    create_experiment, create_experiment_report, create_variant)


class Goal(TestCase):

    pass


class Subject(TestCase):

    pass


class GoalRecord(TestCase):

    def test_unique_together(self):
        goal = create_goal()
        subject = create_subject()
        create_goal_record(goal=goal, subject=subject)

        self.assertRaises(
            IntegrityError, create_goal_record, goal=goal, subject=subject)


class Enrollment(TestCase):

    pass


class Experiment(TestCase):

    pass


class ExperimentReport(TestCase):

    pass


class Variant(TestCase):

    pass
