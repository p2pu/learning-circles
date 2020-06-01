import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-facilitator-feedback');
const surveyId = element.dataset.surveyId;
const studygroup_uuid = element.dataset.studygroupUuid || '';
const studygroup_name = element.dataset.studygroupName || '';
const course = element.dataset.course ? encodeURIComponent(element.dataset.course) : '';
const goal = element.dataset.goal || '';
const goal_rating = element.dataset.goalRating || '';
const attendance_1 = element.dataset.attendance_1 || '';
const attendance_2 = element.dataset.attendance_2 || '';
const attendance_n = element.dataset.attendance_n || '';

const params = {
  studygroup_uuid,
  studygroup_name,
  course,
  goal,
  goal_rating,
  attendance_1,
  attendance_2,
  attendance_n,
};
var queryString = Object.keys(params).map(key => key + '=' + params[key]).join('&');
const url = `https://p2pu.typeform.com/to/${surveyId}?${queryString}`;

const options = {
  onSubmit: () => {
    window.location.href = '/en/facilitator_survey/done/'
  }
}

typeformEmbed.makeWidget(element, url, options);

