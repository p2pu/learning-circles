import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-facilitator-feedback');
const studygroup = element.dataset.studygroup;
const course = element.dataset.studygroupName;
const facilitator = element.dataset.facilitator;
const name = element.dataset.facilitatorName;
const url = `https://p2pu.typeform.com/to/wPg50i?studygroup=${studygroup}&course=${course}&facilitator=${facilitator}&name=${name}`;

const options = {
  onSubmit: () => {
    window.location.href = '/'
  }
}

typeformEmbed.makeWidget(element, url, options);

