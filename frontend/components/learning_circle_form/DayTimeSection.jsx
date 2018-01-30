import React from 'react';
import InputWithLabel from '../common/InputWithLabel';
import SelectWithLabel from '../common/SelectWithLabel';
import moment from 'moment-timezone';

const DayTimeSection = (props) => {
  const timezoneOptions = moment.tz.names().map((tz) => ({value: tz, label: tz }))
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
        placeholder={6}
        name={'weeks'}
        id={'id_weeks'}
        type={'number'}
        errorMessage={props.errors.weeks}
      />
      <InputWithLabel
        label={'What time will your learning circle meet each week?'}
        value={props.learningCircle.meeting_time}
        handleChange={props.updateFormData}
        name={'meeting_time'}
        id={'id_meeting_time'}
        type={'time'}
        errorMessage={props.errors.meeting_time}
      />
      <SelectWithLabel
        label={'What time zone is your learning circle happening in?'}
        value={props.learningCircle.timezone}
        options={timezoneOptions}
        name={'timezone'}
        id={'id_timezone'}
        classes={'form-group input-with-label'}
        onChange={(selected) => { props.updateFormData({ timezone: selected.value })}}
        errorMessage={props.errors.timezone}
      />
      <InputWithLabel
        label={'How long will each session last (in minutes)?'}
        value={props.learningCircle.duration}
        placeholder={90}
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
