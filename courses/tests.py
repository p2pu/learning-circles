from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User

from custom_registration.models import create_user
from courses import models as course_model
from content import models as content_model

from unittest.mock import patch


class CourseTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mail.org'
    test_password = 'testpass'

    test_username2 = 'bob'
    test_email2 = 'bob@mail.org'
    test_password2 = '13245'

    test_title = "A test course"
    test_hashtag = "hashtag"
    test_description = "This is only a test."

    def setUp(self):
        self.client = Client()
        self.locale = 'en'

        self.user = create_user(
            self.test_email,
            self.test_username,
            'lastname',
            self.test_password
        )
        
        self.user2 = create_user(
            self.test_email2,
            self.test_username2,
            'lastname2',
            self.test_password2
        )

        self.course = course_model.create_course(
            **{
                "title": self.test_title,
                "hashtag": self.test_hashtag,
                "description": self.test_description,
                "language": "en",
                "organizer_uri": '/uri/users/testuser',
            }
        )
        content_model.update_content(
            self.course['about_uri'],
            'About',
            'This is the about content',
            '/uri/users/testuser'
        )
        
    def test_course_creation(self):
        course = course_model.create_course(
            **{
                "title": "A test course",
                "hashtag": "ATC-1",
                "description": "This course is all about ABC",
                "language": "en",
                "organizer_uri": '/uri/user/testuser'
            }
        )

        self.assertTrue(not course == None)

        # test that about content was created
        about = content_model.get_content(course['about_uri'])
        self.assertTrue(not about == None)
        self.assertEqual(about['title'], "About")

        self.assertTrue(
            course_model.is_organizer(course['uri'], '/uri/user/testuser')
        )

    def test_course_get(self):
        course = course_model.get_course(self.course['uri'])
        self.assertTrue('id' in course)
        self.assertTrue('uri' in course)
        self.assertTrue('title' in course)
        self.assertTrue('hashtag' in course)
        self.assertTrue('slug' in course)
        self.assertTrue('description' in course)
        self.assertTrue('language' in course)
        self.assertTrue('date_created' in course)
        self.assertTrue('author_uri' in course)
        self.assertTrue('status' in course)
        self.assertTrue('about_uri' in course)
        self.assertTrue('content' in course)


    def test_clone_course(self):
        clone = course_model.clone_course(self.course['uri'], '/uri/user/bob/')
        for key in ['title', 'hashtag', 'description', 'language']:
            self.assertEqual(clone[key], self.course[key])
        self.assertIn('based_on_uri', clone)

        about = content_model.get_content(self.course['about_uri'])
        clone_about = content_model.get_content(clone['about_uri'])
        self.assertEquals(about['content'], clone_about['content'])

        self.assertEqual(len(clone['content']), len(self.course['content']))
        for i in range(len(clone['content'])):
            self.assertEqual(clone['content'][i]['title'], self.course['content'][i]['title'])
            self.assertEqual(clone['content'][i]['content'], self.course['content'][i]['content'])

    def test_delete_spam_course(self):
        course = course_model.create_course(
            **{
                "title": "A test course",
                "hashtag": "ATC-1",
                "description": "This course is all about ABC",
                "language": "en",
                "organizer_uri": '/uri/user/testuser'
            }
        )
        course_model.delete_spam_course(course['uri'])
        with self.assertRaises(course_model.ResourceDeletedException):
            course_model.get_course(course['uri'])

    def test_get_courses(self):
        user = create_user('99@example.com', 'testuser99', 'last', 'password')

        course = course_model.create_course(
            **{
                "title": "A test course",
                "hashtag": "ATC-1",
                "description": "This course is all about ABC",
                "language": "en",
                "organizer_uri": '/uri/user/testuser'
            }
        )
        
        course = course_model.create_course(
            **{
                "title": "A unique test course",
                "hashtag": "AUTC-1",
                "description": "This course is all about ABC",
                "language": "en",
                "organizer_uri": '/uri/user/testuser99'
            }
        )


        # get course by title
        courses = course_model.get_courses(title="A unique test course")
        self.assertEquals(len(courses), 1)

        # get course by user uri
        courses = course_model.get_courses(organizer_uri="/uri/user/testuser99")
        self.assertEquals(len(courses), 1)
