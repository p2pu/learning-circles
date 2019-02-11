import React from 'react';
import SelectWithLabel from 'p2pu-input-fields/dist/SelectWithLabel'
import InputWithLabel from 'p2pu-input-fields/dist/InputWithLabel'
import TimePickerWithLabel from 'p2pu-input-fields/dist/TimePickerWithLabel'
import DatePickerWithLabel from 'p2pu-input-fields/dist/DatePickerWithLabel'
import TimeZoneSelect from 'p2pu-input-fields/dist/TimeZoneSelect'
import moment from 'moment'

const DayTimeSection = (props) => {
  let in4Days = moment().add(4, 'days');
  let dateTimeDisabled = props.learningCircle.draft == false && moment(props.learningCircle.start_date).isBefore(in4Days, 'days');

  return (
    <div>
      <DatePickerWithLabel
        disabled={dateTimeDisabled}
        label={'What is the date of the first learning circle?'}
        value={props.learningCircle.start_date}
        placeholder={'Eg. 6 January, 2018'}
        handleChange={props.updateFormData}
        name={'start_date'}
        id={'id_start_date'}
        type={'date'}
        errorMessage={props.errors.start_date}
        required={true}
        minDate={in4Days}
      />
      <InputWithLabel
        disabled={dateTimeDisabled}
        label={'How many weeks will the learning circle run for?'}
        value={props.learningCircle.weeks}
        handleChange={props.updateFormData}
        name={'weeks'}
        id={'id_weeks'}
        type={'number'}
        min={1}
        errorMessage={props.errors.weeks}
        required={true}
      />
      <TimePickerWithLabel
        disabled={dateTimeDisabled}
        label={'What time will your learning circle meet each week?'}
        open={true}
        handleChange={props.updateFormData}
        name={'meeting_time'}
        id={'id_meeting_time'}
        value={props.learningCircle.meeting_time}
        errorMessage={props.errors.meeting_time}
        required={true}
      />
      <div className={`input-with-label form-group`} >
        <label htmlFor={props.timezone}>What time zone are you in? *</label>
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
        handleChange={props.updateFormData}
        name={'duration'}
        id={'id_duration'}
        type={'number'}
        errorMessage={props.errors.duration}
        required={true}
      />
    </div>
  );
}

export default DayTimeSection;
