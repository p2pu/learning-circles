import pygal
import json
from pygal.style import Style

from studygroups.models import StudyGroup
from studygroups.forms import ApplicationForm

custom_style = Style(
  font_family='Open Sans',
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
  colors=('#05C6B4', '#B7D500', '#FFBC1A', '#FC7100', '#e83e8c'))


class LearnerGoalsChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.Dot(stroke=False, show_legend=False, show_y_guides=False, style=custom_style, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        for choice in ApplicationForm.GOAL_CHOICES:
            data[choice[0]] = []

        signup_questions = self.study_group.application_set.values_list('signup_questions', flat=True)

        # check for responses for field id UXwfFPX0On3f in typeform responses
        # check if the email for those responses already exists in application_set

        for answer_str in signup_questions:
            answer = json.loads(answer_str)
            goal = answer['goals']

            if goal in data:
                data[goal].append(1)
            else:
                data['Other'].append(1)

        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class GoalsMetChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style, show_legend=False, max_scale=5, order_min=0, **kwargs)
        self.chart.x_labels = ["1 (not at all)", "2", "3", "4", "5 (completely)"]
        self.study_group = study_group

    def get_data(self):
        data = { 'Rating': [0,0,0,0,0] }
        learners = self.study_group.application_set
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "G6AXyEuG2NRQ"), None)

            if field is None:
                field = next((answer for answer in answers if answer["field"]["id"] == "IO9ALWvVYE3n"), None)

            if field is not None:
                data['Rating'][field["number"] - 1] += 1

            print(data)

        # G6AXyEuG2NRQ = "When you signed up for {{hidden:course}}, you said that your primary goal was: {{hidden:goal}}. To what extent did you meet your goal?"
        # IO9ALWvVYE3n = "To what extent did you meet your goal?"
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class SkillsLearnedChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style, show_legend = False, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set
        data = {
            "average": [4.29, 3.86, 3.86, 3.71, 3.71, 3.71]
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        labels = {
            "Setting goals for myself": 4.29,
            "Navigating online courses": 3.86,
            "Working with others": 3.86,
            "Feeling connected to my community": 3.71,
            "Speaking in public": 3.71,
            "Using the internet": 3.71
        }

        self.chart.x_labels = list(labels)
        return self.chart.render(is_unicode=True)


class NewLearnersChart():

    def __init__(self, study_group, **kwargs):
        custom_style.value_font_size = 40
        custom_style.title_font_size = 24
        self.chart = pygal.SolidGauge(style=custom_style, inner_radius=0.70, show_legend = False, x_title="of participants were taking a learning circle for the first time", **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'New learners': [{'value': 100, 'max_value': 100}]
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class CompletionRateChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.SolidGauge(style=custom_style, inner_radius=0.70, show_legend = False, x_title="of participants who responded to the survey completed the learning circle", **kwargs)
        self.chart.value_formatter = lambda x: '{:.10g}%'.format(x)
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'Completed': [{'value': 71, 'max_value': 100}]
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class ReasonsForSuccessChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'learner1': "Took on a personal challenge of learning to code.",
            'learner2': "Attended every week to hear the various ways people learn to do this skill.",
            'learner3': "I have a better understanding on how to design a website",
            'learner4': "Had to set a goal for myself",
            'learner5': "Have a degree in web management ecommerce and at the time CDs pages were not introduced",
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class NextStepsChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'learner1': "learn/work IT",
            'learner2': "Use it on the side as extra income",
            'learner3': "Design a website for my business",
            'learner4': "continue learning",
            'learner5': "Create web pages",
            'learner6': "Enroll in continuing education",
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class IdeasChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'learner1': "Furthering in this course of coding.",
            'learner2': "Intermediate or advanced Excel or Access",
            'learner3': "Advance Excel",
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class FacilitatorRatingChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set

        data = {
            'average_rating': 4,
            'maximum': 5
        }

        return data

    def generate(self):
        chart_data = self.get_data()

        remainder = chart_data['maximum'] - chart_data['average_rating']

        stars = "<div class='course-rating row justify-content-around text-warning'>"

        for x in range(0, chart_data['average_rating']):
            stars += "<i class='fas fa-star'></i>"

        for x in range(0, remainder):
            stars += "<i class='far fa-star'></i>"

        return stars + "</div>"
