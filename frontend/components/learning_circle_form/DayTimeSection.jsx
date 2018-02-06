import React from 'react';
import InputWithLabel from '../common/InputWithLabel';
import SelectWithLabel from '../common/SelectWithLabel';
import TimePickerWithLabel from '../common/TimePickerWithLabel';
import TimeZoneSelect from './form_fields/TimeZoneSelect';

const DayTimeSection = (props) => {

  return (
    <div>
      <InputWithLabel
        label={'What is the date of the first learning circle?'}
        value={props.learningCircle.start_date || ''}
        placeholder={'Eg. 6 January, 2018'}
        handleChange={props.updateFormData}
        name={'start_date'}
        id={'id_start_date'}
        type={'date'}
        errorMessage={props.errors.start_date}
      />
      <InputWithLabel
        label={'How many weeks will the learning circle run for?'}
        value={props.learningCircle.weeks}
        handleChange={props.updateFormData}
        defaultValue={6}
        name={'weeks'}
        id={'id_weeks'}
        type={'number'}
        errorMessage={props.errors.weeks}
      />
      <TimePickerWithLabel
        label={'What time will your learning circle meet each week?'}
        open={true}
        handleChange={props.updateFormData}
        name={'meeting_time'}
        id={'id_meeting_time'}
        value={props.learningCircle.meeting_time}
        errorMessage={props.errors.meeting_time}
      />
      <div className={`input-with-label form-group`} >
        <label htmlFor={props.timezone}>What time zone are you in?</label>
        <TimeZoneSelect
          value={props.learningCircle.timezone}
          latitude={props.learningCircle.latitude}
          longitude={props.learningCircle.longitude}
          handleChange={props.updateFormData}
          name={'timezone'}
          id={'id_timezone'}
          errorMessage={props.errors.timezone}
        />
      </div>
      <InputWithLabel
        label={'How long will each session last (in minutes)?'}
        value={props.learningCircle.duration}
        defaultValue={90}
        handleChange={props.updateFormData}
        name={'duration'}
        id={'id_duration'}
        type={'number'}
        errorMessage={props.errors.duration}
      />
    </div>
  );
}

export default DayTimeSection;
