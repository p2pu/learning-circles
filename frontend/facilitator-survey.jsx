import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-facilitator-feedback');
const surveyId = element.dataset.surveyId;
const studygroup_uuid = element.dataset.studygroupUuid || '';
const course = element.dataset.course ? encodeURIComponent(element.dataset.course) : '';
const goal = element.dataset.goal || '';
const rating = element.dataset.goalRating || '';

const url = `https://p2pu.typeform.com/to/${surveyId}?studygroup_uuid=${studygroup_uuid}&course=${course}&goal=${goal}&goal_rating=${rating}`;

const options = {
  onSubmit: () => {
    window.location.href = '/en/facilitator_survey/done/'
  }
}

typeformEmbed.makeWidget(element, url, options);

