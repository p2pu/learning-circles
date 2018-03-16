import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-learner-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.studygroupName);
const email = encodeURIComponent(element.dataset.email);
const goal = element.dataset.goal;
const url = `https://p2pu.typeform.com/to/VA1aVz?studygroup=${studygroup}&course=${course}&email=${email}&goal=${goal}`;

console.log('LEARNER URL', url)

const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

