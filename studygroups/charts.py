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
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from collections import Counter

from studygroups.forms import ApplicationForm
from studygroups.models import StudyGroup
from studygroups.models import Course
from studygroups.models import Meeting
from studygroups.models import Application
from studygroups.models import get_studygroups_with_meetings
from surveys.models import FacilitatorSurveyResponse
from surveys.models import LearnerSurveyResponse
from surveys.models import MAX_STAR_RATING
from surveys.models import learner_survey_summary
from surveys.models import facilitator_survey_summary

import logging

logger = logging.getLogger(__name__)


GOAL_MET_THRESHOLD = 4
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
    answers = response.get('answers', []) # TODO - fixed the error when the key doesn't exist
    return next((answer for answer in answers if answer["field"]["id"] == question_id), None)

def average(total, divisor):
    if divisor == 0:
        return 0

    return round(int(total) / divisor, 2)

def percentage(total, divisor):
    if divisor == 0:
        return 0

    return round((total / divisor) * 100)


def goals_chart(study_group):
    # get all application goals
    applications = study_group.application_set.active()
    goals = [ appl.get_goal() for appl in applications if appl.get_goal() ]
    # add all survey responses for which do do not have goals
    application_ids = [ appl.pk for appl in applications if appl.get_goal() ]
    survey_responses = study_group.learnersurveyresponse_set.exclude(learner__in=application_ids)
    survey_data = map(learner_survey_summary, survey_responses)
    goals += [ response.get("goal") for response in survey_data if response.get("goal")]
    goals = list(set(goals))
    if not len(goals):
        return NO_DATA
    html = "<div><ul class='quote-list list-unstyled'>"
    for goal in goals[:5]:
        html += "<li class='pl-2 my-3 font-italic'>&quot;{}&quot;</li>".format(goal)
    html += "</ul>"
    if len(goals[5:]):
        html += f"<p>and {len(goals[5:])} others</p>"
    return html + "</div>"


def next_steps_chart(study_group):
    html = "<div><ul class='quote-list list-unstyled'>"
    chart_data = map(learner_survey_summary, study_group.learnersurveyresponse_set.all())
    values = [ response.get("next_steps") for response in chart_data if response.get("next_steps")]
    values = list(set(values))
    for value in values[:5]:
        html += "<li class='pl-2 my-3 font-italic'>&quot;{}&quot;</li>".format(value)
    html += "</ul>"
    if len(values[5:]):
        html += f"<p>and {len(values[5:])} others</p>"
    return html + "</div>"


def attendance_chart(study_group):
    # precedence: reported in survey, recorded in weekly feedback
    meetings = study_group.meeting_set.active().order_by('meeting_date', 'meeting_time')
    attendance = [m.feedback_set.first().attendance if m.feedback_set.first() else None for m in meetings]
    survey_responses = study_group.facilitatorsurveyresponse_set.all()
    if survey_responses.count():
        facilitator_survey_response = survey_responses.first()  #TODO there could be more than 1 reply
        attendance_1 = facilitator_survey_response.get_value_by_ref('attendance_1_alt')
        attendance_2 = facilitator_survey_response.get_value_by_ref('attendance_2_alt')
        attendance_n = facilitator_survey_response.get_value_by_ref('attendance_n_alt')
        if attendance_1 and len(attendance):
            attendance[0] = attendance_1
        if attendance_2 and len(attendance) > 1:
            attendance[1] = attendance_2
        if attendance_n and len(attendance) > 2:
            attendance[-1] = attendance_n
        # TODO What happens if there are less than 3 meetings?

    if not sum(filter(lambda i: i, attendance)):
        return NO_DATA

    chart = pygal.Line(style=custom_style(), max_scale=10, order_min=0, y_title="Attendance", range=(0,max(filter(lambda i: i, attendance))))
    chart.show_legend = False
    chart.x_labels = [m.meeting_date for m in meetings]
    chart.add('Attendance', attendance)
    return chart.render(is_unicode=True)


def recommendation_chart(study_group):
    applications = study_group.application_set.active()
    survey_responses = study_group.learnersurveyresponse_set.all()
    survey_data = map(learner_survey_summary, survey_responses)
    recommendations = [ response.get("recommendation_rating") for response in survey_data if response.get("recommendation_rating")]
    if not len(recommendations):
        return NO_DATA
    counts = [ sum(1 for x in recommendations if x == i) for i in range(1,6) ]
    x_title = "Rating (1: No, 3: Maybe, 5: Yes)"
    chart = pygal.Bar(style=custom_style(), show_legend=False, max_scale=10, order_min=0, y_title="Participants", x_title=x_title)
    chart.x_labels = map(str, range(1,6))
    chart.add('Recommendation score', counts)
    return chart.render(is_unicode=True)


def recommendation_reasons_chart(study_group):
    applications = study_group.application_set.active()
    survey_responses = study_group.learnersurveyresponse_set.all()
    survey_data = map(learner_survey_summary, survey_responses)
    why = [
        (r.get("recommendation_rating_reason"), r.get('recommendation_rating'))
        for r in survey_data
        if r.get("recommendation_rating_reason") and r.get('recommendation_rating')
    ]
    why.sort(key=lambda i: i[1])
    why.reverse()
    if not len(why):
        return NO_DATA
    html = "<div>"
    if why:
        html += "<ul class='quote-list list-unstyled'>"
        for value, rating in why[:5]:
            html += "<li class='pl-2 my-3 font-italic'>&quot;{}&quot;</li>".format(value)
        html += "</ul>"
    if len(why[5:]):
        html += f"<p>and {len(why[5:])} others</p>"

    return html + "</div>"


class GoalsMetChart():
    def __init__(self, study_group, **kwargs):
        x_title = "Rating (1: Not at all, 3: Somewhat, 5: Completely)"
        self.chart = pygal.Bar(style=custom_style(), show_legend=False, max_scale=10, order_min=0, y_title="Participants", x_title=x_title, **kwargs)
        self.chart.x_labels = map(str, range(1,6))
        self.study_group = study_group

    def get_data(self):
        """ Combine data from applications and surveys """
        rating_counts = [0]*5
        survey_responses = self.study_group.learnersurveyresponse_set.all()
        survey_summaries = map(learner_survey_summary, survey_responses)
        goal_ratings = [res.get('goal_rating') for res in survey_summaries if res.get('goal_rating')]
        applications = self.study_group.application_set.active().filter(goal_met__isnull=False, learnersurveyresponse__isnull=True)
        goal_ratings += [app.goal_met for app in applications]
        if not len(goal_ratings):
            return None
        for rating in goal_ratings:
            rating_counts[rating-1] += 1

        return { 'Rating': rating_counts }

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


def topic_confidence_chart(study_group):
    survey_data = map(learner_survey_summary, study_group.learnersurveyresponse_set.all())
    ratings = [res.get('subject_confidence') for res in survey_data if res.get('subject_confidence')]
    if not len(ratings):
        return NO_DATA
    counts = [0]*5
    for rating in ratings:
        counts[rating-1] += 1
    x_title = "Confidence (1: No, 3: Somewhat, 5: Yes)"
    chart = pygal.Bar(style=custom_style(), show_legend=False, max_scale=10, order_min=0, y_title="Participants", x_title=x_title)
    chart.x_labels = map(str, range(1,6))
    chart.add('Confidence', counts)
    return chart.render(is_unicode=True)


class NewLearnersChart():
    # TODO - either remove this data or calculate from signup data

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

            if field is not None and field["boolean"] == True:
                first_timers += 1

        value = percentage(first_timers, len(survey_responses))
        data['New learners'][0]['value'] = value

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
            end_date = end_date + relativedelta(months=+2)
            end_date = end_date.replace(day=1) - relativedelta(days=1)

        meetings_count = Meeting.objects.active().filter(meeting_date__gte=start_date, meeting_date__lt=self.report_date, study_group__deleted_at__isnull=True, study_group__draft=False).count()
        data["meetings"].append(meetings_count)

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
        self.chart = pygal.Pie(style=custom_style(), inner_radius=.4, truncate_legend=-1, **kwargs)
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
                    elif country == "" or country is None:
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


class TopTopicsChart():

    def __init__(self, report_date, study_group_ids, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), height=400, show_legend=False, max_scale=5, order_min=0, x_title="Courses with this topic", **kwargs)
        self.study_group_ids = study_group_ids
        self.report_date = report_date

    def get_data(self):
        data = {}
        course_ids = StudyGroup.objects.filter(id__in=self.study_group_ids).values_list('course')
        # TODO topics were renamed to keywords
        course_topics = Course.objects.filter(id__in=course_ids).exclude(keywords="").values_list("keywords")
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
            if topic[0] == "Esol":
                topic_name == "ESOL"
            if topic[0] == "Esl":
                topic_name == "ESL"
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


class TotalLearnersChart():

    def __init__(self, start_time, end_time, **kwargs):
        self.chart = pygal.Line(style=custom_style(), height=400, fill=True, show_legend=False, max_scale=10, order_min=0, y_title="Learners", x_label_rotation=30, **kwargs)
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
            target_path = os.path.join('tmp', filename)
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner goals chart')

        return self.chart.render(is_unicode=True)


class FacilitatorRatingOverTimeChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        style.colors = ["#D3D8E6", "#4c7e80", "#FC7100", "#FFBC1A", "#B7D500", "#05C6B4"]
        self.chart = pygal.StackedBar(style=style, order_min=0, y_title="Number of ratings", x_label_rotation=30, **kwargs)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        data = { None: [] }
        dates = []
        for i in range(1,6):
            data[i] = []

        if self.study_groups.count() < 1:
            return None

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            lcs = self.study_groups.filter(end_date__gte=window_start, end_date__lt=window_end)
            # get rating, presedence: goal_rating > faciltator_rating > survey goal rating
            ratings = list(lcs.filter(facilitator_goal_rating__isnull=False).values_list('facilitator_goal_rating', flat=True))
            ratings += list(lcs.filter(facilitator_goal_rating__isnull=True, facilitator_rating__isnull=False).values_list('facilitator_rating', flat=True))
            #ratings = [s.facilitator_goal_rating if s.facilitator_goal_rating else s.facilitator_rating for s in lcs]
            surveys = FacilitatorSurveyResponse.objects.filter(study_group__in=lcs.filter(facilitator_goal_rating__isnull=True, facilitator_rating__isnull=True))
            surveys = map(facilitator_survey_summary, surveys)
            ratings += [r.get('goal_rating') for r in surveys]
            ratings += [None]*(lcs.count()-len(ratings))  # pad ratings with None's as all other learning circles are considered unrated
            ratings_counter = Counter(ratings)

            for rating, collection in data.items():
                collection.append(ratings_counter[rating])

            dates.append(window_start.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data["data"].items():
            if key is not None:
                key = "{} ★".format(key)
            self.chart.add(str(key), value)

        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-facilitator-ratings.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Facilitator learning circle ratings')

        return self.chart.render(is_unicode=True)



class FacilitatorCourseApprovalChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        style.colors = ["#4c7e80", "#FC7100", "#FFBC1A", "#B7D500", "#05C6B4"]
        self.chart = pygal.StackedBar(style=style, order_min=0, y_title="Number of ratings", x_label_rotation=30, **kwargs)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        data = {}
        dates = []
        for i in range(1,6):
            data[i] = []

        if self.study_groups.count() < 1:
            return None

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            survey_responses = FacilitatorSurveyResponse.objects.filter(study_group__in=self.study_groups, responded_at__gte=window_start, responded_at__lt=window_end)

            ratings = map(facilitator_survey_summary, survey_responses)
            ratings = [r.get('course_rating') for r in ratings if r.get('course_rating')]

            ratings_counter = Counter(ratings)

            for rating, collection in data.items():
                collection.append(ratings_counter[rating])

            dates.append(window_start.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)


        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data["data"].items():
            key = "{} ★".format(key)
            self.chart.add(str(key), value)

        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-facilitator-course-approval.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Facilitator course ratings')

        return self.chart.render(is_unicode=True)


class LearnerCourseApprovalChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        style.colors = ["#4c7e80", "#FC7100", "#FFBC1A", "#B7D500", "#05C6B4"]
        self.chart = pygal.StackedBar(style=style, order_min=0, y_title="Number of ratings", x_label_rotation=30, **kwargs)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        data = {}
        dates = []
        for i in range(1,6):
            data[i] = []

        if self.study_groups.count() < 1:
            return None

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            survey_responses = LearnerSurveyResponse.objects.filter(study_group__in=self.study_groups, responded_at__gte=window_start, responded_at__lt=window_end)

            ratings = map(learner_survey_summary, survey_responses)
            ratings = [r.get('course_rating') for r in ratings if r.get('course_rating')]
            ratings_counter = Counter(ratings)

            for rating, collection in data.items():
                collection.append(ratings_counter[rating])

            dates.append(window_start.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)


        return { "data": data, "dates": dates }


    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data["data"].items():
            key = "{} ★".format(key)
            self.chart.add(str(key), value)

        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-learner-course-approval.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner course approval')

        return self.chart.render(is_unicode=True)


class FacilitatorExperienceChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        self.chart = pygal.StackedLine(style=custom_style(), height=400, fill=True, max_scale=10, order_min=0, y_title="Learning circles started", x_label_rotation=30, **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.study_groups = study_groups

    def get_data(self):
        data = {}
        dates = []

        for i in range(1, 5):
            data[i] = []

        data["5+"] = []

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            study_groups = self.study_groups.filter(start_date__gte=window_start, start_date__lt=window_end)

            counts = []

            for sg in study_groups:
                facilitator = sg.created_by
                # TODO
                sg_count = StudyGroup.objects.published().filter(start_date__lte=sg.start_date, created_by=facilitator).count()
                counts.append(sg_count)

            counter = Counter(counts)

            over_5 = 0

            for count in counter.items():
                label = count[0]
                value = count[1]

                if label > 4:
                    over_5 += value

            for i in range(1, 5):
                value = counter[i]
                data[i].append(value)

            data["5+"].append(over_5)
            dates.append(window_start.strftime("%b %Y"))

            window_start = window_start + relativedelta(months=+1)
            window_end = window_start + relativedelta(months=+1)

        return { "data": data, "dates": dates }


    def generate(self, **opts):
        chart_data = self.get_data()

        for key, value in chart_data["data"].items():
            self.chart.add(str(key), value)

        max_values = [sum(col) for col in zip(*chart_data["data"].values())]

        self.chart.range = (0, max(max_values))
        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-facilitator-experience-chart.png".format(self.end_time.isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learning circles by facilitator experience')

        return self.chart.render(is_unicode=True)


class ParticipantsOverTimeChart():

    def __init__(self, start_time, end_time, study_groups, **kwargs):
        self.chart = pygal.StackedLine(style=custom_style(), height=400, fill=True, max_scale=10, order_min=0, y_title="Participants", x_label_rotation=30, **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.study_groups = study_groups

    def get_data(self):
        data = { "first_time_participants": [], "veteran_participants": [], "dates": [] }
        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            participants = Application.objects.active().filter(accepted_at__gte=window_start, accepted_at__lt=window_end, study_group__in=self.study_groups)

            first_time_participants = 0
            veteran_participants = 0

            for participant in participants:
                if Application.objects.active().filter(accepted_at__lt=window_end, email=participant.email).count() > 1:
                    veteran_participants += 1
                else:
                    first_time_participants += 1

            data["veteran_participants"].append(veteran_participants)
            data["first_time_participants"].append(first_time_participants)
            data["dates"].append(window_end.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return data


    def generate(self, **opts):
        chart_data = self.get_data()

        self.chart.add('First time participants', chart_data["first_time_participants"])
        self.chart.add('Returning participants', chart_data["veteran_participants"])
        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-participants-chart.png".format(self.end_time.isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Participants')

        return self.chart.render(is_unicode=True)


class LearnerGoalsPercentageChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        style.value_font_size = 40
        style.title_font_size = 24
        self.chart = pygal.SolidGauge(style=style, inner_radius=0.70, show_legend = False, x_title="of learners reached their goal", **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_groups = study_groups
        self.end_time = end_time
        self.start_time = start_time

    def get_data(self):
        data = {}
        dates = []

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_end <= self.end_time:
            study_groups = self.study_groups.filter(start_date__gte=window_start, start_date__lt=window_end)

        total_applications_count = Application.objects.active().exclude(goal_met=None).filter(study_group__in=self.study_groups).count()
        goal_met_count = Application.objects.active().exclude(goal_met=None).filter(study_group__in=self.study_groups, goal_met__gte=GOAL_MET_THRESHOLD).count()

        if total_applications_count == 0:
            return None

        percentage = round((goal_met_count / total_applications_count) * 100)
        data['Percentage'][0]['value'] = percentage

        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data.items():
            self.chart.add(key, value)

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-learner-goals-percentage.png".format(self.end_time.isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Percentage of learners who met their goal')

        return self.chart.render(is_unicode=True)


class TopCoursesChart():

    def __init__(self, start_time, end_time, study_groups, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), height=400, show_legend=False, max_scale=5, order_min=0, x_title="Courses with this topic", **kwargs)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        courses = self.study_groups.values_list('course', 'course__title')
        top_courses = Counter(courses).most_common(10)

        return top_courses

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        labels = []
        serie = []

        for item in reversed(chart_data):
            labels.append(item[0][1])
            serie.append(item[1])

        self.chart.x_labels = labels
        self.chart.add("Course", serie)

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-top-courses-chart.png".format(self.end_time.isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Top courses chart')

        return self.chart.render(is_unicode=True)


class MeetingsOverTimeChart():

    def __init__(self, start_time, end_time, **kwargs):
        self.chart = pygal.Line(style=custom_style(), height=400, max_scale=10, order_min=0, y_title="Meetings", x_label_rotation=30, **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.current_year = end_time.year
        self.previous_year = end_time.year - 1

    def get_data(self):
        data = { "current_year": [], "previous_year": [], "dates": [] }

        window_start = datetime.datetime(self.previous_year, 1, 1)
        window_end = window_start + relativedelta(months=+1)
        end_date = datetime.datetime(self.previous_year, 12, 31)

        while window_start <= end_date:
            meetings_count = Meeting.objects.active().filter(meeting_date__gte=window_start, meeting_date__lt=window_end, study_group__deleted_at__isnull=True, study_group__draft=False).count()

            data["dates"].append(window_start.strftime("%b"))
            data["previous_year"].append(meetings_count)

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)


        window_start = self.end_time.replace(month=1, day=1)
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            meetings_count = Meeting.objects.active().filter(meeting_date__gte=window_start, meeting_date__lt=window_end, study_group__deleted_at__isnull=True, study_group__draft=False).count()

            data["current_year"].append(meetings_count)

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return data


    def generate(self, **opts):
        chart_data = self.get_data()

        self.chart.add(str(self.previous_year), chart_data["previous_year"])
        self.chart.add(str(self.current_year), chart_data["current_year"], allow_interruptions=True)
        self.chart.x_labels = chart_data["dates"]

        max_range = max([max(chart_data["previous_year"]), max(chart_data["current_year"])])
        self.chart.range = (0, max_range)

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-meetings-chart.png".format(self.end_time.isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Number of meetings over time')

        return self.chart.render(is_unicode=True)


class StudygroupsByCountryOverTimeChart():

    def __init__(self, start_time, end_time, study_groups, **kwargs):
        self.chart = pygal.StackedLine(style=custom_style(), fill=True, truncate_label=-1, x_label_rotation=30, **kwargs)
        self.start_time = start_time
        self.end_time = end_time
        self.study_groups = study_groups

    def get_data(self):
        data = {}
        dates = []

        countries = self.study_groups.exclude(country_en="").values_list('country_en', flat=True)

        for country in countries:
            data[country] = []

        data["Not reported"] = []

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            studygroups_that_met = get_studygroups_with_meetings(window_start, window_end)

            for country, collection in data.items():
                if country == "Not reported":
                    sgs_count = studygroups_that_met.filter(country_en=None).count()
                else:
                    sgs_count = studygroups_that_met.filter(country_en=country).count()

                data[country].append(sgs_count)

            dates.append(window_start.strftime("%b %Y"))
            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        for key, value in chart_data["data"].items():
            self.chart.add(key, value)

        self.chart.x_labels = chart_data["dates"]

        all_values = chart_data["data"].values()
        logger.debug(all_values)

        months = len(chart_data["dates"])
        monthly_values = [sum([row[i] for row in all_values]) for i in range(months)]
        max_range = max(monthly_values)
        self.chart.range = (0, max_range)

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-countries-chart.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)

            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)

            return "<img src={} alt={} width='100%'>".format(img_url, 'Learning circles by country over time')

        return self.chart.render(is_unicode=True)


class LearnerGoalReachedChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        self.chart = pygal.Bar(style=style, order_min=0, y_title="Number of ratings", x_label_rotation=30, **kwargs)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        data = {}
        dates = []
        for i in range(1,6):
            data[i] = []

        if self.study_groups.count() < 1:
            return None

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            survey_responses = LearnerSurveyResponse.objects.filter(study_group__in=self.study_groups, responded_at__gte=window_start, responded_at__lt=window_end)
            ratings = [
                r.get('goal_rating') for r in map(learner_survey_summary, survey_responses)
                if r.get('goal_rating')
            ]

            ratings_counter = Counter(ratings)

            for rating, collection in data.items():
                collection.append(ratings_counter[rating])

            dates.append(window_start.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        for key, value in chart_data["data"].items():
            self.chart.add(str(key), value)

        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-learner-goals-met.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Rate of learners that met their goals')

        return self.chart.render(is_unicode=True)


class LearnerResponseRateChart():
    def __init__(self, start_time, end_time, study_groups, **kwargs):
        style = custom_style()
        self.chart = pygal.Line(style=style, x_label_rotation=30, range=(0, 100), show_legend=False, **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_groups = study_groups
        self.start_time = start_time
        self.end_time = end_time

    def get_data(self):
        data = []
        dates = []

        if self.study_groups.count() < 1:
            return None

        window_start = self.start_time
        window_end = window_start + relativedelta(months=+1)

        while window_start <= self.end_time:
            applications = Application.objects.filter(study_group__in=self.study_groups, study_group__end_date__gte=window_start, study_group__end_date__lt=window_end)
            applications_with_responses = applications.filter(goal_met__isnull=False)
            # TODO This doesn't take surveys without learned data into account

            value = percentage(applications_with_responses.count(), applications.count())
            data.append(value)
            dates.append(window_start.strftime("%b %Y"))

            window_start = window_end
            window_end = window_start + relativedelta(months=+1)

        return { "data": data, "dates": dates }

    def generate(self, **opts):
        chart_data = self.get_data()

        if chart_data is None:
            return NO_DATA

        self.chart.add("Responded to survey", chart_data["data"])
        self.chart.x_labels = chart_data["dates"]

        if opts.get('output', None) == "png":
            filename = "stats-dash-{}-learner-response-rate.png".format(self.end_time.date().isoformat())
            target_path = os.path.join('tmp', filename)
            self.chart.height = 400
            self.chart.render_to_png(target_path)
            file = open(target_path, 'rb')
            img_url = save_to_aws(file, filename)
            return "<img src={} alt={} width='100%'>".format(img_url, 'Learner response rate')

        return self.chart.render(is_unicode=True)


class OverallRatingBarChart():
    def __init__(self, chart_data, **kwargs):
        style = custom_style()
        style.plot_background = "#F3F4F8"
        style.colors = ["#05C6B4", "#B7D500", "#FFBC1A", "#FC7100", "#4c7e80"]
        style.legend_font_size = 24
        self.chart = pygal.Bar(style=style, height=260, show_legend=False, legend_at_bottom=True, legend_at_bottom_columns=5, show_y_labels=False, **kwargs)
        self.chart_data = chart_data

    def generate(self, **opts):
        colours = ["#05C6B4", "#B7D500", "#FFBC1A", "#FC7100", "#4c7e80"]
        keys = sorted(self.chart_data.keys(), reverse=True)
        labels = [ "{} ★".format(key) for key in keys ]
        serie = [ { "value": self.chart_data[key], "color": colours.pop(0) } for key in keys ]

        self.chart.add("Rating", serie)
        self.chart.x_labels = labels

        return self.chart.render(is_unicode=True)
