import pygal
import json

from pygal.style import Style
from django.utils.translation import ugettext_lazy as _

# from studygroups.forms import ApplicationForm


# TODO how to import this from the ApplicationForm without creating a circular dependency?
GOAL_CHOICES = [
    ('', _('Select one of the following')),
    ('To increase my employability', _('To increase my employability')),
    ('Professional development for my current job', _('Professional development for my current job')),
    ('To accompany other educational programs', _('To accompany other educational programs')),
    ('Personal interest', _('Personal interest')),
    ('Social reasons', _('Social reasons')),
    ('For fun / to try something new', _('For fun / to try something new')),
    ('Other', _('Other')),
]

STAR_RATING_STEPS = 5

theme_colors = ['#05C6B4', '#B7D500', '#FFBC1A', '#FC7100', '#e83e8c']

def rotate_colors():
    theme_colors.append(theme_colors.pop(0))
    colors = theme_colors.copy()
    return colors

def custom_style():
    colors = rotate_colors()

    style = Style(
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

    return round(total / divisor, 2)


class LearnerGoalsChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        for choice in reversed(GOAL_CHOICES):
            data[choice[0]] = 0

        signup_questions = self.study_group.application_set.values_list('signup_questions', flat=True)

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
        labels = chart_data.keys()
        serie = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels

        if opts.get('output', None) == "png":
            filename = "report-{}-learner-goals-chart.png".format(self.study_group.uuid)
            self.chart.render_to_png("/static/images/charts/{}".format(filename))
            return "/images/charts/{}".format(filename)

        return self.chart.render(is_unicode=True)


class GoalsMetChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=10, order_min=0, **kwargs)
        self.chart.x_labels = ["1 (not at all)", "2", "3", "4", "5 (completely)"]
        self.study_group = study_group

    def get_data(self):
        data = { 'Rating': [0,0,0,0,0] }
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return data

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

        for key, value in chart_data.items():
            self.chart.add(key, value)

        if opts.get('output', None) == "png":
            filename = "report-{}-learner-goals-chart.png".format(self.study_group.uuid)
            self.chart.render_to_png("/static/images/charts/{}".format(filename))
            return "/images/charts/{}".format(filename)

        return self.chart.render(is_unicode=True)


class SkillsLearnedChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend = False, max_scale=5, order_min=0, **kwargs)
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
            return data

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
                if field is not None and field['number'] > 3:
                    data[question[1]].append(field['number'])

        return data

    def generate(self):
        chart_data = self.get_data()

        averages = []
        for key, value in chart_data.items():
            total = len(value)
            averages.append(total)

        self.chart.add('Number of learners', averages)
        self.chart.x_labels = list(chart_data)

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
            return data

        first_timers = 0
        for response in survey_responses:
            field = get_response_field(response, "Sj4fL5I6GEei")
            # Sj4fL5I6GEei = "Was this your first learning circle?"

            if field["boolean"] == True:
                first_timers += 1

        percentage = round((first_timers / len(survey_responses)) * 100)
        data['New learners'][0]['value'] = percentage

        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

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
            return data

        completed = 0

        for response_str in survey_responses:
            field = get_response_field(response_str, "i7ps4iNBVya0")
            # i7ps4iNBVya0 = "Which best describes you?"

            if field is not None and field["choice"]["label"] == "I completed the learning circle":
                completed += 1

        percentage = round((completed / len(survey_responses)) * 100)
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
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return data

        for response_str in survey_responses:
            field = get_response_field(response_str, "BBZ52adAzbGJ")
            #BBZ52adAzbGJ = "I succeeded in the learning circle because I..."

            if field is not None:
                response = json.loads(response_str)
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
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return data

        for response_str in survey_responses:
            field = get_response_field(response_str, "qf8iCyr2dw4G")
            #qf8iCyr2dw4G = "What do you want to do with the skills you've developed in the learning circle?"

            if field is not None:
                response = json.loads(response_str)
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
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return data

        for response_str in survey_responses:
            field = get_response_field(response_str, "ll0ZbuEnCkiW")
            #ll0ZbuEnCkiW = "Another topic that I'd like to take a learning circle in is"

            if field is not None:
                response = json.loads(response_str)
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
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, **kwargs)
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
            return data

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

    def generate(self):
        chart_data = self.get_data()
        serie = chart_data.keys()
        labels = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels
        return self.chart.render(is_unicode=True)


class LibraryUsageChart():
    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style(), show_legend=False, max_scale=5, order_min=0, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}

        question_field = get_question_field(self.study_group, "LQGB3S5v0rUk")
        # LQGB3S5v0rUk = "Aside from the learning circle, how often do you visit the library?"
        if question_field is not None:
            choices = question_field['properties']['choices']

            for choice in choices:
                data[choice['label']] = 0

        survey_responses = get_typeform_survey_learner_responses(self.study_group)
        if len(survey_responses) < 1:
            return data

        for response_str in survey_responses:
            field = get_response_field(response_str, "LQGB3S5v0rUk")

            if field is not None:
                label = field['choice'].get('label', None)
                if label in data:
                    data[label] += 1

        return data

    def generate(self):
        chart_data = self.get_data()
        serie = chart_data.keys()
        labels = chart_data.values()

        self.chart.add('Number of learners', serie)
        self.chart.x_labels = labels
        return self.chart.render(is_unicode=True)


class LearnerRatingChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = { 'average_rating': 0, 'maximum': 0 }
        survey_responses = get_typeform_survey_learner_responses(self.study_group)

        if len(survey_responses) < 1:
            return data

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
            return data

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

        if chart_data['maximum'] == 0:
            return "<p>No data</p>"

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
            return data

        response_str = response.response
        field = get_response_field(response_str, "jB4WMEz4S6gt")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data.get('text', None) is None:
            return "<p>No data</p>"

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))


class FacilitatorNewSkillsChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return data

        response_str = response.response
        field = get_response_field(response_str, "TYrhfYZxLH2p")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data.get('text', None) is None:
            return "<p>No data</p>"

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))


class FacilitatorTipsChart():

    def __init__(self, study_group, **kwargs):
        self.study_group = study_group

    def get_data(self):
        data = {}
        response = self.study_group.facilitatorsurveyresponse_set.first()

        if response is None:
            return data

        response_str = response.response
        field = get_response_field(response_str, "dP7B4zDIZRcF")

        if field is not None:
            data['text'] = field['text']

        return data

    def generate(self):
        chart_data = self.get_data()

        if chart_data.get('text', None) is None:
            return "<p>No data</p>"

        return "<ul class='quote-list list-unstyled'><li class='pl-2 my-3 font-italic'>\"{}\"</li></ul>".format(chart_data.get('text'))
