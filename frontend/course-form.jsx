import React from 'react'
import ReactDOM from 'react-dom'
import KeywordInput from './components/keyword-input'
import TopicInput from './components/topic-input'

const element = document.getElementById('div_id_keywords');
let error = element.querySelector('#error_1_id_keywords');
let input = element.querySelector('#id_keywords');
let value = input.value || '';

// Create div and replace form input with div to put KeywordInput into
let div = document.createElement('div');
div.classList.add('keyword-select')
if (error) {
 div.classList.add('is-invalid')
}
input.replaceWith(div);

ReactDOM.render(
  <KeywordInput
    value={value}
    keywords={window.reactData.keywords}
  />,
  div
);

const topicGuidesEl = document.getElementById('div_id_topic_guides');
const options = topicGuidesEl.querySelectorAll('option[selected]');
console.log(options);
let values = [];
options.forEach( ({value, label}) => values.push( { value, label } ));
let topicGuideDiv = document.createElement('div');
topicGuidesEl.querySelector('#id_topic_guides').replaceWith(topicGuideDiv);

ReactDOM.render(
  <TopicInput
    value={values}
    topics={window.reactData.topicGuides}
  />,
  topicGuideDiv
);
