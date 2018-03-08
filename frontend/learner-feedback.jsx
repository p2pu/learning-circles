import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-learner-feedback');
const studygroup = element.dataset.studygroup;
const course = element.dataset.studygroupName;
const url = `https://p2pu.typeform.com/to/VA1aVz?studygroup=${studygroup}&course=${course}`;

const options = {
  onSubmit: () => {
    window.location.href = '/'
  }
}

typeformEmbed.makeWidget(element, url, options);

