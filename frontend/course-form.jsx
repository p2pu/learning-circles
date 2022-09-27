import React from 'react'
import ReactDOM from 'react-dom'
import KeywordInput from './components/keyword-input'
import TopicInput from './components/topic-input'

const element = document.getElementById('div_id_topics');
//let label = element.querySelector('label');
//let hint = element.querySelector('#hint_id_topics');
let error = element.querySelector('#error_1_id_topics');
let input = element.querySelector('#id_topics');
let value = input.value || '';

// Create div and replace form input with div to put TopicInput into
let div = document.createElement('div');
div.classList.add('topics-select')

if (error) {
 div.classList.add('is-invalid')
}

input.replaceWith(div);

ReactDOM.render(
  <KeywordInput
    value={value}
    topics={window.reactData.topics}
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
