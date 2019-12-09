from django.test import TestCase

from studygroups.models import Course
from .community_feedback import calculate_course_ratings


class TestCommunityFeedback(TestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json', 'test_applications.json', 'test_survey_responses.json']

    def test_calculate_course_ratings(self):
        course = Course.objects.get(pk=3)

        self.assertEqual(course.overall_rating, 0)
        self.assertEqual(course.rating_step_counts, "{}")
        self.assertEqual(course.total_ratings, 0)

        calculate_course_ratings(course)

        expected_rating_step_counts = '{"5": 2, "4": 1, "3": 0, "2": 0, "1": 0}'

        self.assertEqual(course.overall_rating, 4.67)
        self.assertEqual(course.rating_step_counts, expected_rating_step_counts)
        self.assertEqual(course.total_ratings, 3)

