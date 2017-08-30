import React from 'react'
import ReactDOM from 'react-dom'
import TopicInput from './components/topic-input'

const element = document.getElementById('div_id_topics');
let label = element.querySelector('.control-label');
let hint = element.querySelector('#hint_id_topics');
let error = element.querySelector('#error_1_id_topics');
let input = element.querySelector('#id_topics');
let value = input.value || '';

ReactDOM.render(
  <TopicInput 
    value={value}
  />,
  element.querySelector('.controls')
);
