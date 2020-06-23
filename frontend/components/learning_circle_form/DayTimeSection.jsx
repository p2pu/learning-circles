import React from 'react';
import {
  InputWithLabel,
  TimePickerWithLabel,
  DatePickerWithLabel,
  TimeZoneSelect
} from 'p2pu-components'
import moment from 'moment'

export default class  DayTimeSection extends React.Component {
  constructor(props){
    super(props);
    this.initialProps = {
      start_date: props.learningCircle.start_date,
      meeting_time: props.learningCircle.meeting_time,
    }
  }

  render(){
    const props = this.props;
    let reminderWarning = null;
    let minDate = new Date();
    let minTime = null;

    if (props.learningCircle.draft == false ){
      let {start_date, meeting_time} = this.initialProps;
      let start_datetime = moment(this.props.learningCircle.start_datetime);
      let plus4Days = moment().add(4, 'days');
      let plus2Days = moment().add(2, 'days');

      if (start_datetime && start_datetime.isBefore(plus2Days)) {
        return (
          <div className='help-text'>
            <div className='content'>
              <p>Your learning circle has already started and you cannot set the date for the whole learning circle anymore. You can still add individual meetings or edit the date and time for meetings. To do this, go to your dashboard to add or edit meetings.</p>
            </div>
          </div>
        );
      }

      if (start_datetime && start_datetime.isBefore(plus4Days)){
        reminderWarning = (
          <div className="form-group">
            <p className="alert alert-warning">Your learning circle is starting in less that 4 days. A reminder has already been generated for the first meeting and will be regenerated if you update the date and/or time. Any edits you have made to the reminder will be lost.</p>
          </div>
        );
      }

      if (start_datetime && start_datetime.isSame(plus2Days, 'days')){
        minTime = meeting_time;
        // TODO time input doesn't support a range
      }

      minDate = plus2Days.toDate();
    }

    return (
      <div>
        {reminderWarning}
        <DatePickerWithLabel
          label={'What is the date of the first learning circle?'}
          value={props.learningCircle.start_date}
          placeholder={'Eg. 2020-06-31'}
          handleChange={props.updateFormData}
          name={'start_date'}
          id={'id_start_date'}
          type={'date'}
          errorMessage={props.errors.start_date}
          required={true}
          minDate={minDate}
          helpText={"The date format is YYYY-MM-DD"}
        />
        <InputWithLabel
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
          label={'What time will your learning circle meet each week?'}
          handleChange={props.updateFormData}
          name={'meeting_time'}
          id={'id_meeting_time'}
          value={props.learningCircle.meeting_time}
          errorMessage={props.errors.meeting_time}
          required={true}
        />
        <TimeZoneSelect
          label={'What time zone are you in?'}
          value={props.learningCircle.timezone}
          latitude={props.learningCircle.latitude}
          longitude={props.learningCircle.longitude}
          handleChange={props.updateFormData}
          name={'timezone'}
          id={'id_timezone'}
          errorMessage={props.errors.timezone}
          required={true}
        />
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
};
