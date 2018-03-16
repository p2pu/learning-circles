import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-learner-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.course);
const contact = encodeURIComponent(element.dataset.contact);
const goalmet = element.dataset.goalMet;
const url = `https://p2pu.typeform.com/to/VA1aVz?studygroup=${studygroup}&course=${course}&contact=${contact}&goalmet=${goalmet}`;

const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

