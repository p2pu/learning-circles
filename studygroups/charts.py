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
  foreground_strong='#000000',
  foreground_subtle='#6c757d',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  colors=('#05C6B4', '#B7D500', '#FFBC1A', '#FC7100', '#e83e8c'))

class LearnerGoalsChart():

    def __init__(self, study_group, **kwargs):
        self.chart = pygal.HorizontalBar(style=custom_style, **kwargs)
        self.study_group = study_group

    def get_data(self):
        data = {}
        learners = self.study_group.application_set
        print(learners)
        data = {
            "Personal interest": 6,
            "Increase employability": 4,
            "Accompany other education programs": 3,
            "Professional development": 1
        }
        return data

    def generate(self):
        # Get chart data
        chart_data = self.get_data()

        # Add data to chart
        for key, value in chart_data.items():
            self.chart.add(key, value)

        # Return the rendered SVG
        return self.chart.render(is_unicode=True)