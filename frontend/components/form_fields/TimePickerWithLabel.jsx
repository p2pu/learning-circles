import React from 'react';
import TimePicker from 'rc-time-picker';
import 'rc-time-picker/assets/index.css';
import moment from 'moment';

const TimePickerWithLabel = (props) => {
  const saveFormat = 'HH:mm';
  const displayFormat = 'h:mm a';

  const onChange = (value) => {
    const time = !!value ? value.format(saveFormat) : null;
    props.handleChange({ [props.name]: time })
  }

  const time = !!props.value ? moment(props.value, saveFormat) : null;

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>{`${props.label} ${props.required ? '*' : ''}`}</label>
      <TimePicker
        showSecond={false}
        use12Hours={true}
        value={time}
        format={displayFormat}
        name={props.name}
        id={props.id}
        onChange={onChange}
        minuteStep={15}
        allowEmpty={true}
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