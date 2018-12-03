
# TODOs:
# - document which survey question each typeform id represents
# - finish adding png condition to all the charts
# - use tempfile module for image files
# - function for generating star rating html
# - function for generating quote list html

import pygal
import json
import os
import boto3
import datetime

from dateutil.relativedelta import relativedelta
from pygal.style import Style
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
from collections import Counter

from studygroups.forms import ApplicationForm
from studygroups.forms import StudyGroup
from studygroups.forms import Course
from studygroups.forms import Meeting

STAR_RATING_STEPS = 5
SKILLS_LEARNED_THRESHOLD = 3
NO_DATA = "<p>No data</p>"

theme_colors = ['#05C6B4', '#B7D500', '#FFBC1A', '#FC7100', '#e83e8c']


def save_to_aws(file_, filename):
    s3 = boto3.resource('s3', aws_access_key_id=settings.P2PU_RESOURCES_AWS_ACCESS_KEY, aws_secret_access_key=settings.P2PU_RESOURCES_AWS_SECRET_KEY)
    key = '/'.join(['learning-circles', filename])
    response = s3.Object(settings.P2PU_RESOURCES_AWS_BUCKET, key).put(Body=file_,  ACL='public-read')
    resource_url = "https://s3.amazonaws.com/{}/{}".format(settings.P2PU_RESOURCES_AWS_BUCKET, key)
    return resource_url

def rotate_colors():
    theme_colors.append(theme_colors.pop(0))
    colors = theme_colors.copy()
    return colors

def custom_style():
    colors = rotate_colors()

    style = Style(
        font_family="'Open Sans', 'Helvetica', 'Arial', sans-serif",
        label_font_size=18.0,
        major_label_font_size=18.0,
        value_font_size=18.0,
        value_label_font_size=18.0,
        tooltip_font_size=18.0,
        title_font_size=18.0,
        legend_font_size=18.0,
        no_data_font_size=18.0,
        background='transparent',
        plot_background='#ffffff',
        foreground='#515665',
        foreground_strong='#515665',
        foreground_subtle='#6c757d',
        opacity='.6',
        opacity_hover='.9',
        transition='400ms ease-in',
        colors=colors)

    return style

def get_typeform_survey_learner_responses(study_group):
    return study_group.learnersurveyresponse_set.values_list('response', flat=True)

def get_typeform_survey_facilitator_responses(study_group):
    return study_group.facilitatorsurveyresponse_set.values_list('response', flat=True)

def get_question_field(study_group, question_id):
    if study_group.learnersurveyresponse_set.count() > 0:
        survey_str = study_group.learnersurveyresponse_set.first().survey
        survey_fields = json.loads(survey_str)['fields']
        return next((field for field in survey_fields if field["id"] == question_id), None)

def get_response_field(response_str, question_id):
    response = json.loads(response_str)
    answers = response['answers']
    return next((answer for answer in answers if answer["field"]["id"] == question_id), None)

def average(total, divisor):
    if divisor == 0:
        return 0

    return round(int(total) / divisor, 2)


class LearnerGoalsChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, x_title="Learners", **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        for choice in reversed(ApplicationForm.GOAL_CHOICES):
            data[choice[0]] = 0

        signup_questions = self.study_group.application_set.values_list('signup_questions', flat=True)
        if len(signup_questions) == 0:
            return None

        # check for responses for field id UXwfFPX0On3f in typeform responses
        # check if the email for those responses already exists in application_set

        for answer_str in signup_questions:
            answer = json.loads(answer_str)
            goal = answer.get('goals', None)

            if goal in data:
                data[goal] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        labels = chart_data.keys()
        serie = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "report-{}-learner-goals-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner goals chart')

        return self.chart.render(is_unicode=True)


class GoalsMetChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=10, order_min=0, x_title="Learners", **kwargs)
        self.chart.x_labels = ["Not at all", "Not very much", "Moderately", "Very much", "Completely"]
        self.study_group = study_group

    def get_data(self):
        data = { 'Rating': [0,0,0,0,0] }
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        # G6AXyEuG2NRQ = "When you signed up for {{hidden:course}}, you said that your primary goal was: {{hidden:goal}}. To what extent did you meet your goal?"
        # IO9ALWvVYE3n = "To what extent did you meet your goal?"

        for response in survey_responses:
            field = get_response_field(response, "G6AXyEuG2NRQ")

            if field is None:
                field = get_response_field(response, "IO9ALWvVYE3n")

            if field is not None:
                data['Rating'][field["number"] - 1] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data.items():
            self.chart.add(key, value)

        if opts.get('output', None) == "png":
            filename = "report-{}-goals-met-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Goal met chart')

        return self.chart.render(is_unicode=True)


class SkillsLearnedChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend = False, max_scale=5, order_min=0, x_title="Learners (multiple selections)", **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {
            "Using the internet": [],
            "Speaking in public": [],
            "Feeling connected to my community": [],
            "Working with others":[],
            "Navigating online courses": [],
            "Setting goals for myself": [],
        }

        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']

            questions = [
                ("QH6akGDy6aHK", "Using the internet"),
                ("itpQxFRlOsOe", "Working with others"),
                ("g0is1ZBXECbh", "Navigating online courses"),
                ("ycB6quFHzH85", "Setting goals for myself"),
                ("zH8IomUmmoaH", "Speaking in public"),
                ("tO3TFJDBmH60", "Feeling connected to my community")
            ]

            for question in questions:
                field = next((answer for answer in answers if answer["field"]["id"] == question[0]), None)
                if field is not None and field['number'] > SKILLS_LEARNED_THRESHOLD:
                    data[question[1]].append(field['number'])

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        averages = []
        for key, value in chart_data.items():
            total = len(value)
            averages.append(total)

        self.chart.add('Number of learners', averages)
        self.chart.x_labels = list(chart_data)

        if opts.get('output', None) == "png":
            filename = "report-{}-skills_learned-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Skills learned chart')

        return self.chart.render(is_unicode=True)


class NewLearnersChart():

    def __init__(self, study_group, **kwargs):
        style = custom_style()
        style.value_font_size = 40
        style.title_font_size = 24
        self.chart = pygal.SolidGauge(style=style, inner_radius=0.70, show_legend = False, x_title="of participants were taking their first learning circle", **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_group = study_group

    def get_data(self):
        data = { 'New learners': [ {'value': 0, 'max_value': 100} ]}
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        first_timers = 0
        for response in survey_responses:
            field = get_response_field(response, "Sj4fL5I6GEei")
            # Sj4fL5I6GEei = "Was this your first learning circle?"

            if field["boolean"] == True:
                first_timers += 1

        percentage = round((first_timers / len(survey_responses)) * 100)
        data['New learners'][0]['value'] = percentage

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data.items():
            self.chart.add(key, value)

        if opts.get('output', None) == "png":
            filename = "report-{}-new-learners-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'New learners chart')

        return self.chart.render(is_unicode=True)


class CompletionRateChart():
    def __init__(self, study_group, **kwargs):
        style = custom_style()
        style.value_font_size = 40
        style.title_font_size = 24
        self.chart = pygal.SolidGauge(style=style, inner_radius=0.70, show_legend = False, x_title="of participants completed the learning circle", **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_group = study_group

    def get_data(self):
        data = { 'Completed': [ {'value': 0, 'max_value': 100} ]}
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        completed = 0

        for response_str in survey_responses:
            field = get_response_field(response_str, "i7ps4iNBVya0")
            # i7ps4iNBVya0 = "Which best describes you?"

            if field is not None and field["choice"]["label"] == "I completed the learning circle":
                completed += 1

        percentage = round((completed / len(survey_responses)) * 100)
        data['Completed'][0]['value'] = percentage

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data.items():
            self.chart.add(key, value)

        if opts.get('output', None) == "png":
            filename = "report-{}-completion-rate-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Completion rate chart')

        return self.chart.render(is_unicode=True)


class ReasonsForSuccessChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        for response_str in survey_responses:
            field = get_response_field(response_str, "BBZ52adAzbGJ")
            #BBZ52adAzbGJ = "I succeeded in the learning circle because I..."

            if field is not None:
                response = json.loads(response_str)
                data[response['landing_id']] = field["text"]

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class NextStepsChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        for response_str in survey_responses:
            field = get_response_field(response_str, "qf8iCyr2dw4G")
            #qf8iCyr2dw4G = "What do you want to do with the skills you've developed in the learning circle?"

            if field is not None:
                response = json.loads(response_str)
                data[response['landing_id']] = field["text"]

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class IdeasChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        for response_str in survey_responses:
            field = get_response_field(response_str, "ll0ZbuEnCkiW")
            #ll0ZbuEnCkiW = "Another topic that I'd like to take a learning circle in is"

            if field is not None:
                response = json.loads(response_str)
                data[response['landing_id']] = field["text"]

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class PromotionChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, x_title="Learners", **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = { 'Other': 0 }

        question_field = get_question_field(self.study_group, "lYX1qfcSKARQ")
        if question_field is not None:
            choices = question_field['properties']['choices']

            for choice in choices:
                data[choice['label']] = 0

        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        for response_str in survey_responses:
            field = get_response_field(response_str, "lYX1qfcSKARQ")

            if field is not None:
                selections = field['choices'].get('labels', None)
                if selections is not None:
                    for label in selections:
                        if label in data:
                            data[label] += 1
                else:
                    selection = field['choices'].get('other', None)
                    if selection is not None:
                        data['Other'] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        serie = chart_data.values()
        labels = chart_data.keys()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "report-{}-promotion-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Promotion chart')

        return self.chart.render(is_unicode=True)


class LibraryUsageChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, x_title="Learners", **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}

        survey_responses = get_typeform_survey_learner_responses(self.study_group)
        if len(survey_responses) < 1:
            return None

        question_field = get_question_field(self.study_group, "LQGB3S5v0rUk")
        # LQGB3S5v0rUk = "Aside from the learning circle, how often do you visit the library?"
        if question_field is not None:
            choices = question_field['properties']['choices']

            for choice in choices:
                data[choice['label']] = 0

        for response_str in survey_responses:
            field = get_response_field(response_str, "LQGB3S5v0rUk")

            if field is not None:
                label = field['choice'].get('label', None)
                if label in data:
                    data[label] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        serie = chart_data.values()
        labels = chart_data.keys()

        if sum(serie) == 0:
            return None

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "report-{}-library-usage-chart.png".format(self.study_group.uuid)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Library usage chart')

        return self.chart.render(is_unicode=True)


class LearnerRatingChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = { 'average_rating': 0, 'maximum': 0 }
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return None

        ratings = []

        for response_str in survey_responses:
            field = get_response_field(response_str, "iGWRNCyniE7s")
            # iGWRNCyniE7s = "How well did the online course {{hidden:course}} work as a learning circle?"
            if field is not None:
                ratings.append(field['number'])

        average_rating = average(sum(ratings), len(ratings))

        data = {
            'average_rating': int(average_rating),
            'maximum': 5
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        remainder = chart_data['maximum'] - chart_data['average_rating']

        stars = "<div class='course-rating row justify-content-around text-warning'>"

        for x in range(0, chart_data['average_rating']):
            stars += "<i class='fas fa-star'></i>"

        for x in range(0, remainder):
            stars += "<i class='far fa-star'></i>"

        return stars + "</div>"


class FacilitatorRatingChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = { 'average_rating': 0, 'maximum': 0 }
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return None

        survey_questions = response.survey
        survey_responses = get_typeform_survey_facilitator_responses(self.study_group)

        ratings = []

        for response_str in survey_responses:
            field = get_response_field(response_str, "Zm9XlzKGKC66")
            # Zm9XlzKGKC66 = "How well did the online course {{hidden:course}} work as a learning circle?"
            if field is not None:
                ratings.append(field['number'])

        average_rating = average(sum(ratings), len(ratings))

        survey_fields = json.loads(survey_questions)['fields']
        selected_field = next((field for field in survey_fields if field["id"] == "Zm9XlzKGKC66"), None)
        steps = selected_field['properties']['steps']

        # Make sure rating is out of 5
        if steps > STAR_RATING_STEPS:
            multiplier = STAR_RATING_STEPS / steps
            steps = STAR_RATING_STEPS
            average_rating = average_rating * multiplier

        data = {
            'average_rating': round(average_rating),
            'maximum': steps
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        remainder = chart_data['maximum'] - chart_data['average_rating']

        stars = "<div class='course-rating row justify-content-around text-warning'>"

        for x in range(0, chart_data['average_rating']):
            stars += "<i class='fas fa-star'></i>"

        for x in range(0, remainder):
            stars += "<i class='far fa-star'></i>"

        return stars + "</div>"


class AdditionalResourcesChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return None

        response_str = response.response
        field = get_response_field(response_str, "jB4WMEz4S6gt")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))


class FacilitatorNewSkillsChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return None

        response_str = response.response
        field = get_response_field(response_str, "TYrhfYZxLH2p")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))


class FacilitatorTipsChart():
    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return None

        response_str = response.response
        field = get_response_field(response_str, "dP7B4zDIZRcF")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))


class LearningCircleMeetingsChart():

    def __init__(self, report_date, **kwargs):
        self.chart = pygal.Line(style=custom_style(), height=400, fill=True, show_legend=False, max_scale=10, order_min=0, y_title="Meetings", x_label_rotation=30, **kwargs)
        self.report_date = report_date

    def get_data(self):
        data = { "meetings": [], "dates": [] }
        start_date = datetime.date(2016, 1, 1)
        end_date = datetime.date(2016, 1, 31)

        while end_date <= self.report_date:
            meetings_count = Meeting.objects.active().filter(meeting_date__gte=start_date, meeting_date__lt=end_date, study_group__deleted_at__isnull=True, study_group__draft=False).count()
            if end_date.month % 3 == 1:
                data["dates"].append(end_date.strftime("%b %Y"))
            else:
                data["dates"].append("")
            data["meetings"].append(meetings_count)
            end_date = end_date + relativedelta(months=+1)

        return data


    def generate(self, **opts):
        chart_data = self.get_data()

        self.chart.add('Number of meetings', chart_data["meetings"])
        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "community-digest-{}-meetings-chart.png".format(self.report_date.isoformat())
            target_path = os.path.join('/tmp', filename)
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner goals chart')

        return self.chart.render(is_unicode=True)


class LearningCircleCountriesChart():

    def __init__(self, start_date, report_date, **kwargs):
        self.chart = pygal.Pie(style=custom_style(), inner_radius=.4, **kwargs)
        self.start_date = start_date
        self.report_date = report_date

    def get_data(self):
        data = { "Not reported": 0 }

        studygroups = StudyGroup.objects.published()

        for sg in studygroups:
            first_meeting = sg.first_meeting()
            last_meeting = sg.last_meeting()

            if first_meeting is not None and last_meeting is not None:
                if (first_meeting.meeting_date >= self.start_date and first_meeting.meeting_date <= self.report_date)\
                or (last_meeting.meeting_date >= self.start_date and last_meeting.meeting_date <= self.report_date)\
                or (first_meeting.meeting_date <= self.start_date and last_meeting.meeting_date >= self.report_date):
                    country = sg.country_en
                    country = "USA" if country == "United States of America" else country

                    country = "USA" if country == "United States of America" else country

                    if country in data:
                        data[country] += 1
                    elif country is "" or country is None:
                        data["Not reported"] += 1
                    else:
                        data[country] = 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            if key != "Not reported":
                label = "{} ({})".format(key, value)
                self.chart.add(label, value)

        self.chart.add("Not reported", chart_data["Not reported"])

        if opts.get('output', None) == "png":
            filename = "community-digest-{}-countries-chart.png".format(self.report_date.isoformat())
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)

            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner goals chart')

        return self.chart.render(is_unicode=True)


class NewLearnerGoalsChart():

    def __init__(self, report_date, applications, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), height=400, show_legend=False, order_min=0, max_scale=10, x_title="Learners", **kwargs)
        self.applications = applications
        self.report_date = report_date

    def get_data(self):
        data = {}
        for choice in reversed(ApplicationForm.GOAL_CHOICES):
            data[choice[0]] = 0

        signup_questions = self.applications.values_list('signup_questions', flat=True)

        for answer_str in signup_questions:
            answer = json.loads(answer_str)
            goal = answer.get('goals', None)

            if goal in data:
                data[goal] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()
        labels = chart_data.keys()
        serie = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "community-digest-{}-learner-goals-chart.png".format(self.report_date.isoformat())
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner Goals')

        return self.chart.render(is_unicode=True)


class TopTopicsChart():

    def __init__(self, report_date, study_group_ids, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), height=400, show_legend=False, max_scale=5, order_min=0, x_title="Courses with this topic", **kwargs)
        self.study_group_ids = study_group_ids
        self.report_date = report_date

    def get_data(self):
        data = {}
        course_ids = StudyGroup.objects.filter(id__in=self.study_group_ids).values_list('course')
        course_topics = Course.objects.filter(id__in=course_ids).exclude(topics="").values_list("topics")
        topics = [
            item.strip().lower().capitalize() for sublist in course_topics for item in sublist[0].split(',')
        ]

        top_topics = Counter(topics).most_common(10)
        for topic in reversed(top_topics):
            topic_name = topic[0]
            if topic[0] == "Html":
                topic_name = "HTML"
            if topic[0] == "Css":
                topic_name = "CSS"
            data[topic_name] = topic[1]

        return data

    def generate(self, **opts):
        chart_data = self.get_data()
        labels = chart_data.keys()
        serie = chart_data.values()

        self.chart.add('Courses tagged', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "community-digest-{}-top_topics-chart.png".format(self.report_date.isoformat())
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Top 10 Topics')

        return self.chart.render(is_unicode=True)



class NewLearnersGoalsChart():
    def __init__(self, start_time, end_time, applications, team=None, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, x_title="Learners", **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.applications = applications
        self.team = team

    def get_data(self):
        data = {}
        for choice in reversed(ApplicationForm.GOAL_CHOICES):
            data[choice[0]] = 0

        if self.applications.count() == 0:
            return None

        for application in self.applications:
            answer = json.loads(application.signup_questions)
            goal = answer.get('goals', None)

            if goal in data:
                data[goal] += 1

        return data

    def generate(self, **opts):
        chart_data = self.get_data()
        if chart_data is None:
            return NO_DATA

        labels = chart_data.keys()
        serie = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            team = self.team.id if self.team else 'staff'
            filename = "weekly-update-{}-{}-learner-goals-chart.png".format(self.end_time.isoformat(), team)
            target_path = os.path.join('/tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner goals chart')

        return self.chart.render(is_unicode=True)

