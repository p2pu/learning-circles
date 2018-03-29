import * as typeformEmbed from '@typeform/embed';
import { FACILITATOR_SURVEY, NO_STUDYGROUP_SURVEY } from './constants'

const element = document.getElementById('studygroup-facilitator-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.studygroupName);
const facilitator = encodeURIComponent(element.dataset.facilitator);
const name = encodeURIComponent(element.dataset.facilitatorName);
const rating = element.dataset.rating;
const surveyId = element.dataset.nostudygroup === "true" ? NO_STUDYGROUP_SURVEY : FACILITATOR_SURVEY;

const url = `https://p2pu.typeform.com/to/${surveyId}?studygroup=${studygroup}&course=${course}&facilitator=${facilitator}&name=${name}&rating=${rating}`;

const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

