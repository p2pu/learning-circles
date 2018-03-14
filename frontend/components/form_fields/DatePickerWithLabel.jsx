import React from 'react';
import DatePicker from 'react-datepicker';
import moment from 'moment';

import 'react-datepicker/dist/react-datepicker.css';

const DatePickerWithLabel = (props) => {
  const onChange = (value) => {
    const date = !!value ? value.format('YYYY-MM-DD') : null;
    props.handleChange({ [props.name]: date })
  }

  const date = !!props.value ? moment(props.value) : null;

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>{`${props.label} ${props.required ? '*' : ''}`}</label>
      <DatePicker
        selected={date}
        name={props.name}
        id={props.id}
        onChange={onChange}
        className="form-control"
      />
      {
        props.errorMessage &&
        <div className='error-message minicaps'>
          { props.errorMessage }
        </div>
      }
    </div>
  )
}

export default DatePickerWithLabel;