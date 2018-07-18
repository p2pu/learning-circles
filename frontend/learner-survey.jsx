import * as typeformEmbed from '@typeform/embed';
import { LEARNER_SURVEY } from './constants'

const element = document.getElementById('studygroup-learner-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.course);
const contact = encodeURIComponent(element.dataset.contact);
const goal = encodeURIComponent(element.dataset.goal);
const learner = encodeURIComponent(element.dataset.learnerName)
const facilitator = encodeURIComponent(element.dataset.facilitatorName)
const goalmet = element.dataset.goalMet;
const url = `https://p2pu.typeform.com/to/${LEARNER_SURVEY}?studygroup=${studygroup}&course=${course}&contact=${contact}&goalmet=${goalmet}&goal=${goal}&learner=${learner}&facilitator=${facilitator}`;


const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

