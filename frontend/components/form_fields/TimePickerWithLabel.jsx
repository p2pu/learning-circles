import React from 'react';
import TimePicker from 'rc-time-picker';
import 'rc-time-picker/assets/index.css';
import moment from 'moment';

const TimePickerWithLabel = (props) => {
  const onChange = (value) => {
    const time = !!value ? value.format('h:mm a') : null;
    props.handleChange({ [props.name]: time })
  }

  const format = 'h:mm a';
  const time = !!props.value ? moment(props.value, 'h:mm a') : moment().hour(0).minute(0);

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>{`${props.label} ${props.required ? '*' : ''}`}</label>
      <TimePicker
        showSecond={false}
        use12Hours={true}
        value={time}
        format={format}
        name={props.name}
        id={props.id}
        onChange={onChange}
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

export default TimePickerWithLabel;