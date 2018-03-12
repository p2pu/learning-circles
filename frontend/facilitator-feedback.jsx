import * as typeformEmbed from '@typeform/embed';

const element = document.getElementById('studygroup-facilitator-feedback');
const studygroup = element.dataset.studygroup;
const course = encodeURIComponent(element.dataset.studygroupName);
const facilitator = encodeURIComponent(element.dataset.facilitator);
const name = encodeURIComponent(element.dataset.facilitatorName);
const url = `https://p2pu.typeform.com/to/wPg50i?studygroup=${studygroup}&course=${course}&facilitator=${facilitator}&name=${name}`;

console.log('FACILITATOR URL', url)

const options = {
  onSubmit: () => {
    window.location.href = 'done'
  }
}

typeformEmbed.makeWidget(element, url, options);

