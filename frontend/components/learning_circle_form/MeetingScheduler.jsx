import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { render } from 'react-dom';
import { RRule, RRuleSet, rrulestr } from 'rrule'
import DayPicker, { DateUtils } from 'react-day-picker';
import Modal from 'react-responsive-modal';
import moment from 'moment'

import {
  InputWithLabel,
  TimePickerWithLabel,
  DatePickerWithLabel,
  TimeZoneSelect,
  SelectWithLabel,
} from 'p2pu-components'

import 'react-day-picker/lib/style.css';

/*

WTF are we doing with dates

the DB stores local dates as a date string formatted as YYYY-MM-DD

the DayPicker (calendar) should display local dates

dates need to be converted to UTC for rrule to generate the rules


==== Creating new LC ====
user selects local start date
we convert it to UTC for rrule
rrule returns a collection of dates in UTC
we convert them to local time to display
we convert them to date string to send to DB

=== Editing existing meetings ====

convert meeting date string to local date for display
convert to UTC if editing recurrence using rrule
convert back to local time for display
convert back to date string for DB

*/



const weekdays = [
  { label: 'Sunday', value: RRule.SU },
  { label: 'Monday', value: RRule.MO },
  { label: 'Tuesday', value: RRule.TU },
  { label: 'Wednesday', value: RRule.WE },
  { label: 'Thursday', value: RRule.TH },
  { label: 'Friday', value: RRule.FR },
  { label: 'Saturday', value: RRule.SA },
]

const defaultRecurrenceRules = {
  meetingCount: 6,
  frequency: 'weekly',
}

class MeetingScheduler extends React.Component {
  constructor(props) {
    super(props)
    this.initialState = {
      meetings: props.learningCircle.meetings ? props.learningCircle.meetings.map(m => JSON.parse(m)['meeting_date']) : [],
      patternString: '',
      showModal: false,
      recurrenceRules: defaultRecurrenceRules
    }
    this.state = this.initialState
  }

  // date conversion utils

  localDateToUtcDate = (localDate) => {
    const date = new Date(localDate)
    const UTCDate = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(), date.getUTCMinutes()))
    return utcDate
  }

  utcDateToLocalDate = (utcDate, tz) => {
    const options = {
      year: '2-digit', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      timeZone: tz || Intl.DateTimeFormat().resolvedOptions().timeZone,
      timeZoneName: 'short'
    }
    const formatter = new Intl.DateTimeFormat('default', options)

    return formatter.format(utcDate)
  }

  dateObjectToStringForDB = (date) => {
    const year = date.getFullYear()
    const month = `0${date.getMonth() + 1}`.slice(-2)
    const day = `0${date.getDate()}`.slice(-2)

    return `${year}-${month}-${day}`
  }

  dbDateStringToLocalDate = (dateStr, timeStr="00:00") => {
    const [year, month, day] = dateStr.split('-')
    const [hour, minute] = timeStr.split(':')
    const date = new Date(year, month-1, day, hour, minute)

    return date
  }

  // recurrence modal functions

  resetState = () => this.setState(this.initialState)
  openModal = () => this.setState({ ...this.state, showModal: true })
  closeModal = () => this.setState({ ...this.state, showModal: false })

  generateMeetings = () => {
    if (!learningCircle['start_date']) { return }
    const date = dbDateStringToUtcDate(learningCircle['start_date'], learningCircle['meeting_time'])
    let opts = {
      dtstart: date,
      count: parseInt(recurrenceRules.meetingCount),
    }

    if (recurrenceRules.frequency === 'weekly') {
      opts.freq = RRule.WEEKLY
      opts.interval = 1
      opts.byweekday = recurrenceRules.weekday
    } else if (recurrenceRules.frequency === 'biweekly') {
      opts.freq = RRule.WEEKLY
      opts.interval = 2
      opts.byweekday = recurrenceRules.weekday
    }

    const rule = new RRule(opts)
    const recurringMeetings = rule.all()
    const pattern = rule.toText()

    setState({
      ...state,
      pattern,
      showModal: false,
      meetings: recurringMeetings
    })
  }


  // input handlers

  handleChange = (newContent) => {
    let presets = {};
    let newState = {
      ...state
    }

    const key = Object.keys(newContent)[0]
    if (key === 'start_date') {
      const [year, month, day] = newContent.start_date.split('-')
      const [hour, minute] = learningCircle['meeting_time'] ? learningCircle['meeting_time'].split(':') : ['00', '00']
      const date = new Date(year, month-1, day, hour, minute)
      presets.weekday = [weekdays[date.getDay()].value]
      newState.meetings = [date]
    }


    newState.content = {
      ...content,
      ...newContent,
      ...presets,
    }

    setState(newState)
    props.updateFormData({ ...newContent })
  }

  handleDayClick = (day, { selected, disabled }) => {
    if (disabled) {
      return;
    }
    const selectedDays = [...meetings]
    const isStartDate = selectedDays.length === 0

    if (isStartDate) {
      const formattedDate = dateObjectToStringForDB(day)
      handleChange({ start_date: formattedDate })
    }

    if (selectedDays.length > 0) {
      const selectedIndex = selectedDays.findIndex(meeting =>
        DateUtils.isSameDay(meeting, day)
      );

      if (selectedIndex >= 0) {
        selectedDays.splice(selectedIndex, 1);
      } else {
        selectedDays.push(day);
      }

      setState({
        ...state,
        meetings: selectedDays,
        pattern: 'Custom selection'
      });
    }
  }

  render() {
    const { resetState, openModal, closeModal, handleChange, handleDayClick, generateMeetings } = this;
    const { patternString, showModal, recurrenceRules, meetings } = this.state;
    const { learningCircle, errors, updateFormData } = this.props
    let reminderWarning = null;
    let minDate = null;
    let minTime = null;

    if (learningCircle.draft == false ){
      let {start_date, meeting_time} = this.props;
      let start_datetime = moment(learningCircle.start_datetime);
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
            <p className="alert alert-warning">Your learning circle is starting in less than 4 days. A reminder has already been generated for the first meeting and will be regenerated if you update the date and/or time. Any edits you have made to the reminder will be lost.</p>
          </div>
        );
      }

      if (start_datetime && start_datetime.isSame(plus2Days, 'days')){
        minTime = meeting_time;
        // TODO time input doesn't support a range
      }

      minDate = plus2Days.toDate();
    }

    return(
      <div className="">
        {reminderWarning}

        <div className="meeting-scheduler mb-4">

          <div className="form">
            <DatePickerWithLabel
              handleChange={handleChange}
              helpText="Enter a date below or select one on the calendar"
              required
              label={'What is the date of the first learning circle?'}
              value={learningCircle.start_date}
              placeholder={'Eg. 2020-06-31'}
              name={'start_date'}
              id={'id_start_date'}
              type={'date'}
              errorMessage={errors.start_date}
              required={true}
              minDate={minDate}
            />

            {
              learningCircle["start_date"] &&
              <button className="p2pu-btn dark" onClick={openModal}>Schedule recurring meetings</button>
            }

          </div>

          <div className="row calendar my-3">
            <div className="col-12 col-lg-6 d-flex justify-content-center" style={{ flex: '1 1 auto' }}>
              <DayPicker
                selectedDays={meetings.map((m => new Date(m.toString())))}
                onDayClick={handleDayClick}
                disabledDays={{ before: new Date() } }
              />
            </div>

            <div className="col-12 col-lg-6 d-flex justify-content-center">
              <div className="selected-dates p-4" style={{ paddingTop: '20px' }}>
                <label
                  htmlFor="selected-dates"
                  className='input-label left text-bold'
                >
                { `Selected dates (${meetings.length})` }
                </label>
                <p className="d-flex align-center">
                  {
                    meetings.length > 0 &&
                    <span className="material-icons" style={{ fontSize: '20px', paddingTop: '2px', paddingRight: '6px' }}>
                      date_range
                    </span>
                  }
                  <span className="capitalize" style={{ lineHeight: '1.5' }}>{patternString}</span>
                </p>
                <ul id="selected-dates" className="list-unstyled">
                  {
                    meetings.sort((a,b) => {
                      return a - b
                    }).map(meeting => <li key={meeting.toString()} className="mb-2">{meeting.toLocaleString('default', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })}</li>)
                  }
                </ul>
              </div>
            </div>
          </div>
          <button className="p2pu-btn dark" onClick={resetState}>Clear dates</button>
        </div>

        <TimePickerWithLabel
          label={'What time will your learning circle meet each week?'}
          handleChange={updateFormData}
          name={'meeting_time'}
          id={'id_meeting_time'}
          value={learningCircle.meeting_time}
          errorMessage={errors.meeting_time}
          required={true}
        />
        <TimeZoneSelect
          label={'What time zone are you in?'}
          value={learningCircle.timezone}
          latitude={learningCircle.latitude}
          longitude={learningCircle.longitude}
          handleChange={updateFormData}
          name={'timezone'}
          id={'id_timezone'}
          errorMessage={errors.timezone}
          required={true}
        />
        <InputWithLabel
          label={'How long will each session last (in minutes)?'}
          value={learningCircle.duration}
          handleChange={updateFormData}
          name={'duration'}
          id={'id_duration'}
          type={'number'}
          errorMessage={errors.duration}
          required={true}
          min={0}
        />

        <Modal open={showModal || false} onClose={closeModal} classNames={{modal: 'p2pu-modal', overlay: 'modal-overlay'}}>

          <div className="">
            <div className="mb-3 heading" role="heading"><h3>Recurring meetings</h3></div>
            <SelectWithLabel
              options={[
                { label: 'Monday', value: RRule.MO },
                { label: 'Tuesday', value: RRule.TU },
                { label: 'Wednesday', value: RRule.WE },
                { label: 'Thursday', value: RRule.TH },
                { label: 'Friday', value: RRule.FR },
                { label: 'Saturday', value: RRule.SA },
                { label: 'Sunday', value: RRule.SU }
              ]}
              name='weekday'
              value={recurrenceRules['weekday']}
              handleChange={handleChange}
              label="On which days will you meet?"
              isMulti={true}
              isClearable={false}
            />
            <SelectWithLabel
              options={[
                { label: 'Every week', value: 'weekly' },
                { label: 'Every 2 weeks', value: 'biweekly' },
              ]}
              name='frequency'
              value={recurrenceRules['frequency']}
              handleChange={handleChange}
              label="How often will you meet?"
              isClearable={false}
            />
            <InputWithLabel
              name="meetingCount"
              label="How many times will you meet?"
              value={recurrenceRules['meetingCount']}
              handleChange={handleChange}
              type={'number'}
            />
            <div className="d-flex justify-content-between buttons">
              <button className="p2pu-btn dark" onClick={closeModal}>Select custom dates</button>
              <button className="p2pu-btn blue" onClick={generateMeetings}>Schedule meetings</button>
            </div>
          </div>
        </Modal>
      </div>
    );
  }
}


MeetingScheduler.propTypes = {
  updateFormData: PropTypes.func.isRequired,
  learningCircle: PropTypes.object.isRequired,
  errors: PropTypes.object,
}

export default MeetingScheduler;


