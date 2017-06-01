import React from 'react'
import ReactDOM from 'react-dom'
import MobileInput from './components/mobile-input'

const element = document.getElementById('div_id_mobile');
let label = element.querySelector('.control-label');
let hint = element.querySelector('#hint_id_mobile');
let error = element.querySelector('#error_1_id_mobile');
let input = element.querySelector('#id_mobile');

ReactDOM.render(
  <MobileInput 
    label={label.textContent}
    hint={hint.textContent}
    error={error?error.textContent:null}
    value={input.value}
  />,
  document.getElementById('div_id_mobile')
);
