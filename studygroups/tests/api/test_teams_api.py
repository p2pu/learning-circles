# coding: utf-8
from django.conf import settings
from django.test import TestCase, override_settings
from django.test import Client
from django.contrib.auth.models import User, Group

from studygroups.models import StudyGroup
from studygroups.models import Team

import json

class TestTeamsApi(TestCase):

    fixtures = ['test_courses.json', 'test_studygroups.json', 'test_teams.json']

    def test_list_teams(self):
        c = Client()
        response = c.get('/api/teams/')
        self.assertEqual(response.status_code, 200)

        res_data = response.json()

        self.assertEqual(res_data["count"], 2)

        # complete team - pk 1

        item_fields = [
            'id',
            'name',
            'page_slug',
            'member_count',
            'studygroup_count',
            'zoom',
            'coordinates',
            'organizers',
            'image_url',
            'date_established'
        ]

        resp_keys = list(res_data["items"][1].keys())
        for key in resp_keys:
            self.assertIn(key, item_fields)
        for key in item_fields:
            self.assertIn(key, resp_keys)

        # incomplete_team - pk 2

        item_fields = [
            'id',
            'name',
            'page_slug',
            'member_count',
            'studygroup_count',
            'zoom',
            'date_established',
            'organizers'
        ]

        resp_keys = list(res_data["items"][0].keys())
        for key in resp_keys:
            self.assertIn(key, item_fields)
        for key in item_fields:
            self.assertIn(key, resp_keys)


    def test_team_data(self):
        c = Client()
        response = c.get('/api/teams/')
        self.assertEqual(response.status_code, 200)

        res_data = response.json()
        self.assertEqual(res_data["count"], 2)

        team_json = res_data["items"][1]

        team = Team.objects.get(pk=1)
        organizer = User.objects.get(pk=1)
        organizer_studygroups_count = StudyGroup.objects.filter(facilitator=organizer).count()

        self.assertEqual(team_json["member_count"], team.teammembership_set.active().count())
        self.assertEqual(team_json["organizers"][0]["first_name"], organizer.first_name)
        self.assertEqual(team_json["studygroup_count"], organizer_studygroups_count)
        self.assertEqual(team_json["image_url"], f"{settings.PROTOCOL}://{settings.DOMAIN}" + team.page_image.url)

