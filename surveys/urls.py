from django.urls import re_path

from studygroups.decorators import user_is_staff
from studygroups.decorators import user_is_group_facilitator
from . import views

urlpatterns = [
    re_path(
        r'^learning-circle/export/$',
        user_is_staff(views.ExportLearnerSurveysView.as_view()),
        name='survey_learner_responses_csv'
    ),
    re_path(
        r'^learning-circle/(?P<study_group_id>[\d]+)/export/$',
        user_is_group_facilitator(views.ExportLearnerSurveysView.as_view()),
        name='survey_learning_circle_learner_responses_csv'
    ),
    re_path(
        r'^facilitator/export/$',
        views.ExportFacilitatorSurveysView.as_view(),
        name='survey_facilitator_responses_csv'
    ),
]



