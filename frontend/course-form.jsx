import React from 'react'
import ReactDOM from 'react-dom'
import TopicInput from './components/topic-input'

const element = document.getElementById('div_id_topics');
//let label = element.querySelector('label');
//let hint = element.querySelector('#hint_id_topics');
//let error = element.querySelector('#error_1_id_topics');
let input = element.querySelector('#id_topics');
let value = input.value || '';

// Create div and replace form input with div to put TopicInput into
let div = document.createElement('div');
input.replaceWith(div);

ReactDOM.render(
  <TopicInput 
    value={value}
    topics={window.reactData.topics}
  />,
  div
);
