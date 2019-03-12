from django.test import TestCase

from studygroups.models import Course
from .community_feedback import calculate_course_ratings
from .community_feedback import calculate_course_tagdorsements


class TestCommunityFeedback(TestCase):
    fixtures = ['test_courses.json', 'test_studygroups.json', 'test_applications.json', 'test_survey_responses.json']

    def test_calculate_course_ratings(self):
        course = Course.objects.get(pk=3)

        self.assertEqual(course.overall_rating, 0)
        self.assertEqual(course.rating_step_counts, "{}")
        self.assertEqual(course.total_ratings, None)

        calculate_course_ratings(course)

        expected_rating_step_counts = '{"5": 2, "4": 1, "3": 0, "2": 0, "1": 0}'

        self.assertEqual(course.overall_rating, 4.67)
        self.assertEqual(course.rating_step_counts, expected_rating_step_counts)
        self.assertEqual(course.total_ratings, 3)

    def test_calculate_course_tagdorsements(self):
        course = Course.objects.get(pk=3)

        self.assertEqual(course.tagdorsement_counts, "{}")
        self.assertEqual(course.tagdorsements, "")
        self.assertEqual(course.total_reviewers, None)

        calculate_course_tagdorsements(course)

        self.assertEqual(course.tagdorsement_counts, '{"Easy to use": 1, "Good for first time facilitators": 0, "Great for beginners": 1, "Engaging material": 1, "Learners were very satisfied": 1, "Led to great discussions": 1}')
        self.assertEqual(course.tagdorsements, 'Easy to use, Great for beginners, Engaging material, Learners were very satisfied, Led to great discussions')
        self.assertEqual(course.total_reviewers, 1)
