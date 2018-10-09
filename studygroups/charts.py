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
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "G6AXyEuG2NRQ"), None)

            if field is None:
                field = next((answer for answer in answers if answer["field"]["id"] == "IO9ALWvVYE3n"), None)

            if field is not None:
                data['Rating'][field["number"] - 1] += 1

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
        data = { 'New learners': [ {'value': 0, 'max_value': 100} ]}
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        first_timers = 0

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "Sj4fL5I6GEei"), None)
            # Sj4fL5I6GEei = "Was this your first learning circle?"

            if field["boolean"] == True:
                first_timers += 1

        percentage = (first_timers / len(survey_responses)) * 100
        data['New learners'][0]['value'] = percentage

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
        data = { 'Completed': [ {'value': 0, 'max_value': 100} ]}
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        completed = 0

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "i7ps4iNBVya0"), None)
            # i7ps4iNBVya0 = "Which best describes you?"

            if field["choice"]["label"] == "I completed the learning circle":
                completed += 1

        percentage = (completed / len(survey_responses)) * 100
        data['Completed'][0]['value'] = percentage

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
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "BBZ52adAzbGJ"), None)
            #BBZ52adAzbGJ = "I succeeded in the learning circle because I..."

            if field is not None:
                data[response['landing_id']] = field["text"]

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
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "qf8iCyr2dw4G"), None)
            #qf8iCyr2dw4G = "What do you want to do with the skills you've developed in the learning circle?"

            if field is not None:
                data[response['landing_id']] = field["text"]

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
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "ll0ZbuEnCkiW"), None)
            #ll0ZbuEnCkiW = "Another topic that I'd like to take a learning circle in is"

            if field is not None:
                data[response['landing_id']] = field["text"]

        return data

    def generate(self):
        chart_data = self.get_data()

        quotes = "<ul class='quote-list list-unstyled'>"

        for key, value in chart_data.items():
            quotes += "<li class='pl-2 my-3 font-italic'>\"{}\"</li>".format(value)

        return quotes + "</ul>"


class PromotionChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.Dot(stroke=False, show_legend=False, show_y_guides=False, style=custom_style, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = { 'Other': [] }

        survey_str = self.study_group.learnersurveyresponse_set.first().survey
        survey_fields = json.loads(survey_str)['fields']
        promo_field = next((field for field in survey_fields if field["id"] == "lYX1qfcSKARQ"), None)
        choices = promo_field['properties']['choices']

        for choice in choices:
            data[choice['label']] = []

        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "lYX1qfcSKARQ"), None)
            if field is not None:
                selections = field['choices'].get('labels', None)

            if selections is not None:
                for label in selections:
                    if label in data:
                        data[label].append(1)
            else:
                selection = field['choices'].get('other', None)
                if selection is not None:
                    data['Other'].append(1)

        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class LibraryUsageChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.Dot(stroke=False, show_legend=False, show_y_guides=False, style=custom_style, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}

        survey_str = self.study_group.learnersurveyresponse_set.first().survey
        survey_fields = json.loads(survey_str)['fields']
        choices = survey_fields
        promo_field = next((field for field in survey_fields if field["id"] == "LQGB3S5v0rUk"), None)
        # LQGB3S5v0rUk = "Aside from the learning circle, how often do you visit the library?"
        choices = promo_field['properties']['choices']

        for choice in choices:
            data[choice['label']] = []

        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "LQGB3S5v0rUk"), None)
            if field is not None:
                label = field['choice'].get('label', None)

            if label is not None:
                if label in data:
                    data[label].append(1)

        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class LearnerRatingChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        survey_responses = self.study_group.learnersurveyresponse_set.values_list('response', flat=True)

        ratings = []

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "iGWRNCyniE7s"), None)
            # iGWRNCyniE7s = "How well did the online course {{hidden:course}} work as a learning circle?"
            if field is not None:
                ratings.append(field['number'])

        average_rating = sum(ratings) / len(ratings)

        print(average_rating)

        data = {
            'average_rating': int(round(average_rating)),
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


class FacilitatorRatingChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        survey_questions = self.study_group.facilitatorsurveyresponse_set.first().survey
        survey_responses = self.study_group.facilitatorsurveyresponse_set.values_list('response', flat=True)

        ratings = []

        for response_str in survey_responses:
            response = json.loads(response_str)
            answers = response['answers']
            field = next((answer for answer in answers if answer["field"]["id"] == "Zm9XlzKGKC66"), None)
            # Zm9XlzKGKC66 = "How well did the online course {{hidden:course}} work as a learning circle?"
            if field is not None:
                ratings.append(field['number'])

        average_rating = sum(ratings) / len(ratings)

        survey_fields = json.loads(survey_questions)['fields']
        selected_field = next((field for field in survey_fields if field["id"] == "Zm9XlzKGKC66"), None)
        steps = selected_field['properties']['steps']

        print(average_rating)

        data = {
            'average_rating': int(round(average_rating)),
            'maximum': steps
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
