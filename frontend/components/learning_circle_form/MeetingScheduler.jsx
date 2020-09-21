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

Notes about dates
=================

- the DB stores local dates as a date string formatted as YYYY-MM-DD
- the DayPicker (calendar) displays local dates
- dates need to be converted to UTC for rrule

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
      patternString: 'Custom selection',
      showModal: false,
      recurrenceRules: defaultRecurrenceRules
    }
    this.state = this.initialState
  }

  componentDidUpdate(prevProps) {
    if (this.props.learningCircle.start_date && prevProps.learningCircle.start_date !== this.props.learningCircle.start_date) {
      const localDate = this.dbDateStringToLocalDate(this.props.learningCircle.start_date)
      this.setState({
        ...this.state,
        recurrenceRules: {
          ...this.state.recurrenceRules,
           weekday: [weekdays[localDate.getDay()].value]
        }
      })
    }
  }

  // date conversion utils

  localDateToUtcDate = (localDate) => {
    const utcDate = new Date(Date.UTC(localDate.getUTCFullYear(), localDate.getUTCMonth(), localDate.getUTCDate(), localDate.getUTCHours(), localDate.getUTCMinutes()))
    return utcDate
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

  dbDateStringToUtcDate = (dateStr, timeStr="00:00") => {
    const [year, month, day] = dateStr.split('-')
    const [hour, minute] = timeStr.split(':')
    const date = new Date(Date.UTC(year, month-1, day, hour, minute))

    return date
  }

  meetingsToOrderedDates = (meetings) => {
    const dates = meetings.map(m => this.dbDateStringToLocalDate(m))
    return dates.sort((a,b) => (a - b))
  }

  // recurrence modal functions

  openModal = () => this.setState({ ...this.state, showModal: true })
  closeModal = () => this.setState({ ...this.state, showModal: false })

  generateMeetings = () => {
    const { learningCircle } = this.props;
    const { recurrenceRules } = this.state;

    if (!learningCircle['start_date']) { return }

    const formattedStartDate = learningCircle['start_date']
    const timeString = learningCircle['meeting_time']
    const startDate = this.dbDateStringToLocalDate(formattedStartDate, timeString)
    const utcDate = this.localDateToUtcDate(startDate)

    let opts = {
      dtstart: utcDate,
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
    const patternString = rule.toText()
    const meetingDates = recurringMeetings.map(m => this.dateObjectToStringForDB(m))

    this.setState({
      ...this.state,
      patternString,
      showModal: false,
    })

    this.props.updateFormData({ meetings: meetingDates })
  }


  // input handlers

  handleChange = (newContent) => {
    const key = Object.keys(newContent)[0]
    if (key === 'start_date') {
      this.setState({
        showModal: true
      })
    }
    this.props.updateFormData({ ...newContent, meetings: [ newContent.start_date ] })
  }

  handleRRuleChange = newContent => {
    this.setState({
      ...this.state,
      recurrenceRules: {
        ...this.state.recurrenceRules,
        ...newContent
      }
    })
  }

  handleDayClick = (day, { selected, disabled }) => {
    if (disabled) {
      return;
    }
    const selectedDays = [...this.props.learningCircle.meetings]
    const isFirstDate = selectedDays.length === 0

    if (isFirstDate) {
      const formattedDate = this.dateObjectToStringForDB(day)
      this.handleChange({ start_date: formattedDate })
    } else {
      const formattedDate = this.dateObjectToStringForDB(day)
      const selectedIndex = selectedDays.findIndex(meeting =>
        meeting === formattedDate
      );

      if (selectedIndex >= 0) {
        selectedDays.splice(selectedIndex, 1);
      } else {
        selectedDays.push(formattedDate);
      }

      const meetingDates = this.meetingsToOrderedDates(selectedDays)
      const formattedStartDate = this.dateObjectToStringForDB(meetingDates[0])
      this.props.updateFormData({ start_date: formattedStartDate })

      this.setState({
        ...this.state,
        patternString: 'Custom selection'
      });

      this.props.updateFormData({ meetings: selectedDays })
    }
  }

  clearDates = () => {
    this.setState({ ...this.state, patternString: 'Custom selection', recurrenceRules: defaultRecurrenceRules })
    this.props.updateFormData({ "start_date": '', meetings: [] })
  }

  render() {
    const { clearDates, openModal, closeModal, handleChange, handleRRuleChange, handleDayClick, generateMeetings, dbDateStringToLocalDate } = this;
    const { patternString, showModal, recurrenceRules } = this.state;
    const { learningCircle, errors, updateFormData } = this.props;
    const { meetings } = learningCircle;

    const displayMeetings = meetings.map(m => dbDateStringToLocalDate(m, learningCircle.meeting_time))
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
                selectedDays={displayMeetings}
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
                { `Selected dates (${displayMeetings.length})` }
                </label>
                {
                  displayMeetings.length > 0 &&
                  <p className="d-flex align-center">
                    <span className="material-icons" style={{ fontSize: '20px', paddingTop: '2px', paddingRight: '6px' }}>
                      date_range
                    </span>
                    <span className="capitalize" style={{ lineHeight: '1.5' }}>{patternString}</span>
                  </p>
                }
                <ul id="selected-dates" className="list-unstyled">
                  {
                    displayMeetings.sort((a,b) => {
                      return a - b
                    }).map(meeting => <li key={meeting.toString()} className="mb-2">{meeting.toLocaleString('default', { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })}</li>)
                  }
                </ul>
              </div>
            </div>
          </div>
          <button className="p2pu-btn dark" onClick={clearDates}>Clear dates</button>
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
              handleChange={handleRRuleChange}
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
              handleChange={handleRRuleChange}
              label="How often will you meet?"
              isClearable={false}
            />
            <InputWithLabel
              name="meetingCount"
              label="How many times will you meet?"
              value={recurrenceRules['meetingCount']}
              handleChange={handleRRuleChange}
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


