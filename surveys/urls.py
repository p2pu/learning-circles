from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^learning-circle/export/$',
        views.ExportLearnerSurveysView.as_view(),
        name='survey_learner_responses_csv'
    ),
    url(
        r'^learning-circle/(?P<study_group_id>[\d]+)/export/$',
        views.ExportLearnerSurveysView.as_view(),
        name='survey_learning_circle_learner_responses_csv'
    ),
    url(
        r'^facilitator/export/$',
        views.ExportFacilitatorSurveysView.as_view(),
        name='survey_facilitator_responses_csv'
    ),
]



