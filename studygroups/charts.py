import pygal
from pygal.style import Style

from studygroups.models import StudyGroup

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
        learners = self.study_group.application_set

        #TODO this is so dumb lolol
        data = {
            "Personal interest": [1,1,1,1,1,1],
            "Increase employability": [1,1,1,1],
            "Accompany other education programs": [1,1,1],
            "Professional development": [1]
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class GoalsMetChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.Bar(style=custom_style, show_y_guides=False, show_y_labels=False, show_legend=False, **kwargs)
        self.chart.x_labels = ["1", "2", "3", "4", "5"]
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set
        data = {
            "Rating": [0, 0, 3, 1, 1]
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

        return self.chart.render(is_unicode=True)


class SkillsLearnedChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set
        data = {
            "Setting goals for myself": 4.29,
            "Navigating online courses": 3.86,
            "Working with others": 3.86,
            "Feeling connected to my community": 3.71,
            "Speaking in public": 3.71,
            "Using the internet": 3.71
        }
        return data

    def generate(self):
        chart_data = self.get_data()

        for key, value in chart_data.items():
            self.chart.add(key, value)

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
