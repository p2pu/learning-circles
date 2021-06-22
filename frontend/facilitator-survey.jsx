import * as typeformEmbed from '@typeform/embed';
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const element = document.getElementById('studygroup-facilitator-feedback');
const surveyId = element.dataset.surveyId;
const studygroup_uuid = element.dataset.studygroupUuid || '';
const studygroup_name = element.dataset.studygroupName || '';
const course = element.dataset.course ? encodeURIComponent(element.dataset.course) : '';
const goal = element.dataset.goal || '';
const attendance_1 = element.dataset.attendance_1 || '';
const attendance_2 = element.dataset.attendance_2 || '';
const attendance_n = element.dataset.attendance_n || '';
let goal_rating = element.dataset.goalRating || '';

// check if goal_rating is part of the window.location.search
// if so and goal_rating is not set or different, do a post to update
const urlParams = new URL(window.location.href).searchParams;
const goal_rating_qs = urlParams.get('goal_rating');
if (goal_rating_qs && goal_rating_qs != goal_rating){
  goal_rating = goal_rating_qs;
  // post goal_rating to backend
  data = {
    facilitator_goal_rating: goal_rating,
  };
  axios(element.dataset.postRatingUrl, {method: 'PUT', data: _formData}).then(res => {
  }).catch(err => {
  });

}

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

