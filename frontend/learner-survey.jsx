import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-learner-feedback');
const surveyId = element.dataset.surveyId;
const studygroupUuid = element.dataset.studygroupUuid;
const studygroupName = element.dataset.studygroupName;
const course = encodeURIComponent(element.dataset.course);
const contact = encodeURIComponent(element.dataset.contact);
const goalRating = encodeURIComponent(element.dataset.goalRating);
const learnerUuid = element.dataset.learnerUuid
const facilitator = encodeURIComponent(element.dataset.facilitatorName)
const goalmet = element.dataset.goalMet;
const url = `https://p2pu.typeform.com/to/${surveyId}?studygroup_uuid=${studygroupUuid}&studygroup_name=${studygroupName}&course=${course}&goal_rating=${goalRating}&learner_uuid=${learnerUuid}&facilitator=${facilitator}`;


const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

