import React from 'react'
import ReactDOM from 'react-dom'
import CourseInput from './components/course-input'

const element = document.getElementById('div_id_course');
let label = element.querySelector('label');
let hint = element.querySelector('#hint_id_course');
let error = element.querySelector('#error_1_id_course');
let input = element.querySelector('#id_course');
let value = input.value || '';
let q = input.selectedIndex>0?input.options[input.selectedIndex].innerHTML:'';

ReactDOM.render(
  <CourseInput 
    label={label.textContent}
    hint={hint?hint.textContent:null}
    error={error?error.textContent:null}
    value={value}
    q={q}
  />,
  element
);
