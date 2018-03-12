import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-learner-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.studygroupName);
const url = `https://p2pu.typeform.com/to/VA1aVz?studygroup=${studygroup}&course=${course}`;

console.log('LEARNER URL', url)

const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

