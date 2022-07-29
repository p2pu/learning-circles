import React from 'react';
import axios from 'axios';

import FormContainer from './learning_circle_form/FormContainer';
import HelpContainer from './learning_circle_form/HelpContainer';
import RegistrationModal from './learning_circle_form/RegistrationModal';
import Alert from './learning_circle_form/Alert';
import ApiHelper from '../helpers/ApiHelper'

import {
  LC_PUBLISHED_PAGE,
  FACILITATOR_PAGE,
  LC_DEFAULTS,
  DESKTOP_BREAKPOINT
} from '../helpers/constants';

import './stylesheets/learning-circle-form.scss';
import 'p2pu-components/dist/build.css';

function dateObjectToStringForDB(date){
  if (!date || typeof(date) !== 'object') {
    throw Error("No Date object provided")
  }
  const year = date.getFullYear()
  const month = `0${date.getMonth() + 1}`.slice(-2)
  const day = `0${date.getDate()}`.slice(-2)
  const hours = `0${date.getHours()}`.slice(-2)
  const minutes = `0${date.getMinutes()}`.slice(-2)

  return { meeting_date: `${year}-${month}-${day}`, meeting_time: `${hours}:${minutes}` };
}

function parseMeetingDate(meetingObj){
  const parsedMeeting = JSON.parse(meetingObj)
  const [year, month, day] = parsedMeeting['meeting_date'].split('-')
  const [hour, minute] = parsedMeeting['meeting_time'].split(':')
  const date = new Date(year, month-1, day, hour, minute)
  return date
}

export default class CreateLearningCirclePage extends React.Component {
  static defaultProps = {
    learningCircle: LC_DEFAULTS
  }

  constructor(props){
    super(props);
    console.log(this.props.learningCircle)
    const meetings = this.props.learningCircle.meetings.map(m => parseMeetingDate(m)).sort((a,b) => a - b)
    this.state = {
      currentTab: 0,
      learningCircle: {
        ...this.props.learningCircle,
        meetings: meetings
      },
      team: this.props.team,
      showModal: false,
      showHelp: window.screen.width > DESKTOP_BREAKPOINT,
      user: this.props.user,
      userId: this.props.userId,
      errors: {},
      alert: { show: false },
      isSaving: false,
      isPublishing: false,
    };
    this.changeTab = (tab) => this._changeTab(tab);
    this.onSubmitForm = (val) => this._onSubmitForm(val);
    this.onCancel = () => this._onCancel();
    this.toggleHelp = () => this._toggleHelp();
    this.showModal = () => this._showModal();
    this.closeModal = () => this._closeModal();
    this.closeAlert = () => this._closeAlert();
    this.showAlert = (msg, type) => this._showAlert(msg, type);
    this.updateFormData = (data, cb) => this._updateFormData(data, cb);
    this.registerUser = () => this._registerUser();
    this.onLogin = (user) => this._onLogin(user);
    this.allTabs = [
      '1. Course',
      '2. Location',
      '3. Day & Time',
      '4. Customize',
      '5. Finalize',
    ];
  }

  componentDidMount() {
    const urlParams = new URL(window.location.href).searchParams;
    let courseId;

    if (this.props.learningCircle.reminders_edited){
      this.showAlert(`You have previously edited reminder messages for future meetings. Updating the learning circle name or venue information will cause the reminders to be regenerated and your edits will be lost.`, 'warning');
    }


    if (urlParams.get('course_id')) {
      courseId = urlParams.get('course_id')
    } else if (this.props.learningCircle && this.props.learningCircle.course) {
      if (typeof(this.props.learningCircle.course) === 'number') {
        courseId = this.props.learningCircle.course
      } else if (typeof(this.props.learningCircle.course) === 'object') {
        courseId = this.props.learningCircle.course.id
      }
    }

    if (!!courseId) {
      const api = new ApiHelper('courses', window.location.origin);
      const params = { course_id: courseId }
      const callback = (response, _opts) => {
        const course = response.items[0];
        if (!course) {
          this.setState({
            alert: {
              show: true,
              type: 'danger',
              message: `There is no course with the ID ${courseId}.`
            }
          })
        } else {
          this.setState({
            learningCircle: {
              ...this.state.learningCircle,
              course
            }
          })
        }
      }
      const opts = { params, callback }

      api.fetchResource(opts)
    }
  }

  _updateFormData(data, callback=null) {
    this.setState({
      learningCircle: {
        ...this.state.learningCircle,
        ...data
      }
    }, callback)
  }

  _toggleHelp() {
    this.setState({ showHelp: !this.state.showHelp })
  }

  _changeTab(tab) {
    const newTab = !!this.allTabs[tab] ? tab : 0;
    this.setState({ currentTab: newTab });
  }

  _showModal() {
    this.setState({ showModal: true })
  }

  _closeModal() {
    this.setState({ showModal: false })
  }

  _showAlert(message, type) {
    this.setState({
      alert: {
        message,
        type,
        show: true
      }
    })
  }

  _closeAlert() {
    this.setState({ alert: { show: false }})
  }

  extractPlaceData = place => {
    if (!place) return null

    const country = place.country ? place.country.default : null;
    const country_en = place.country && place.country.en ? place.country.en : country;
    const placeData = {
      city: place.locale_names.default[0],
      region: place.administrative ? place.administrative[0] : null,
      country: country,
      country_en: country_en,
      latitude: place._geoloc ? place._geoloc.lat : null,
      longitude: place._geoloc ? place._geoloc.lng : null,
      place_id: place.objectID ? place.objectID : null,
      place: null, // remove Algolia place object
    }

    return placeData
  }

  formatMeetingDates = () => {
    return this.state.learningCircle.meetings.map(m=> dateObjectToStringForDB(m))
  }

  _onSubmitForm(draft=true) {
    if (!this.state.user) {
      this.showModal();
    } else {
      this.setState({ isSaving: draft, isPublishing: !draft })
      const placeData = this.extractPlaceData(this.state.learningCircle.place)
      let start_date = this.state.learningCircle.start_date;
      if (start_date && start_date instanceof Date){
        start_date = dateObjectToStringForDB(start_date)['meeting_date'];
      }
      const meetings = this.formatMeetingDates()

      const data = {
        ...this.state.learningCircle,
        ...placeData,
        course: this.state.learningCircle.course.id,
        draft: draft,
        meetings: meetings,
        start_date: start_date
      }

      console.log("post data", data)

      const onSuccess = (data) => {
        this.setState({ learningCircle: {}, isSaving: false, isPublishing: false }, () => {
          window.location.href = data.studygroup_url;
        })
      }

      const onError = (data) => {
        console.log(`Error saving the learning circle: ${JSON.stringify(data.errors)}`)
        this.setState({
          isSaving: false,
          isPublishing: false,
          currentTab: 0,
          errors: data.errors,
          learningCircle: {
            ...this.state.learningCircle,
            draft: true
          }
        })

        const msg = 'There was a problem saving your learning circle. Please check the error messages in the form and make the necessary changes.'
        const type = 'danger'
        this.showAlert(msg, type)
      }

      const onFail = (err) => {
        const msg = 'There was an error saving your learning circle. Please try again.'
        const type = 'danger'
        this.showAlert(msg, type)
        this.setState({ isSaving: false, isPublishing: false })
      }

      const opts = { data, onSuccess, onError, onFail };
      const api = new ApiHelper('learningCircles', window.location.origin);

      if (this.state.learningCircle.id) {
        api.updateResource(opts, this.state.learningCircle.id)
      } else {
        api.createResource(opts);
      }
    }
  }

  _onCancel() {
    window.location.href = FACILITATOR_PAGE;
  }

  _onLogin(user) {
    this.setState({ user });
    this.showAlert("You're logged in! You can now save or publish your learning circle.", 'success')

    // TODO: remove this when we switch to the React component for the account in the navbar
    const accountLink = document.querySelector('nav .nav-items .account a');
    accountLink.setAttribute('href', '/en/accounts/logout');
    accountLink.innerText = 'Log out';
  }

  render() {
    return (
      <div className='page-container'>
        <Alert
          show={this.state.alert.show}
          type={this.state.alert.type}
          closeAlert={this.closeAlert}>
          {this.state.alert.message}
        </Alert>
        <div className='help-toggle' onClick={this.toggleHelp}>
          <i className="material-icons">{ this.state.showHelp ? window.screen.width < DESKTOP_BREAKPOINT ? 'close' : 'exit_to_app' : 'info_outline' }</i>
          <small className='minicaps'>{ this.state.showHelp ? 'hide' : 'info' }</small>
        </div>
        <FormContainer
          updateFormData={this.updateFormData}
          showHelp={this.state.showHelp}
          toggleHelp={this.toggleHelp}
          currentTab={this.state.currentTab}
          allTabs={this.allTabs}
          changeTab={this.changeTab}
          userId={this.props.userId}
          learningCircle={this.state.learningCircle}
          team={this.state.team}
          errors={this.state.errors}
          onCancel={this.onCancel}
          onSubmitForm={this.onSubmitForm}
          isSaving={this.state.isSaving}
          isPublishing={this.state.isPublishing}
          showAlert={this.showAlert}
          tinymceScriptSrc={this.props.tinymceScriptSrc}
        />
        <HelpContainer currentTab={this.state.currentTab} />
        <RegistrationModal
          open={this.state.showModal}
          closeModal={this.closeModal}
          user={this.props.user}
          onLogin={this.onLogin}
          showAlert={this.showAlert}
        />
      </div>
    );
  }
}
