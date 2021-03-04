import React from 'react'
import ReactDOM from 'react-dom'
import CharacterCountInput from './components/character-count-input'

const element = document.getElementById('div_id_sms_body');
let error = element.querySelector('#error_1_id_sms_body');
let input = element.querySelector('#id_sms_body');
let value = input.value || '';

// Create div and replace form input with div to put TopicInput into
let div = document.createElement('div');
div.classList.add('character_count_input')

if (error) {
 div.classList.add('is-invalid')
}
input.replaceWith(div);

ReactDOM.render(
  <CharacterCountInput
    name="sms_body"
    value={value}
    maxLength={input.maxLength}
    error={error}
  />,
  div
);
