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
} from '../constants';

import './stylesheets/learning-circle-form.scss'


export default class CreateLearningCirclePage extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      currentTab: 0,
      learningCircle: !!this.props.learningCircle ? this.props.learningCircle : LC_DEFAULTS,
      showModal: false,
      showHelp: window.screen.width > DESKTOP_BREAKPOINT,
      user: this.props.user,
      errors: {},
      alert: { show: false }
    };
    this.changeTab = (tab) => this._changeTab(tab);
    this.onSubmitForm = (val) => this._onSubmitForm(val);
    this.onCancel = () => this._onCancel();
    this.toggleHelp = () => this._toggleHelp();
    this.showModal = () => this._showModal();
    this.closeModal = () => this._closeModal();
    this.closeAlert = () => this._closeAlert();
    this.updateFormData = (data, cb) => this._updateFormData(data, cb);
    this.registerUser = () => this._registerUser();
    this.onLogin = (user) => this._onLogin(user);
    this.allTabs = {
      0: '1. Course',
      1: '2. Location',
      2: '3. Day & Time',
      3: '4. Customize',
      4: '5. Finalize'
    };
  }

  componentDidMount() {
    const urlParams = new URL(window.location.href).searchParams;
    const courseId = !!this.props.learningCircle ? this.props.learningCircle.course : urlParams.get('course_id');

    if (!!courseId) {
      const api = new ApiHelper('courses');
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

  _closeAlert() {
    this.setState({ alert: { show: false }})
  }

  _onSubmitForm() {
    if (this.state.user) {
      const data = {
        ...this.state.learningCircle,
        course: this.state.learningCircle.course.id
      }

      const onSuccess = (data) => {
        this.setState({ learningCircle: {} }, () => {
          if (data.published) {
            window.location.href = `${LC_PUBLISHED_PAGE}?url=${data.study_group_url}`;
          } else {
            window.location.href = FACILITATOR_PAGE;
          }
        })
      }

      const onError = (data) => {
        this.setState({
          currentTab: 0,
          errors: data.errors,
          alert: {
            show: true,
            type: 'danger',
            message: 'There was a problem saving your learning circle. Please check the error messages in the form and make the necessary changes.'
          },
          learningCircle: {
            ...this.state.learningCircle,
            published: false
          }
        })
      }

      const onFail = (err) => {
        console.log(err)
        this.setState({
          alert: {
            show: true,
            type: 'danger',
            message: 'There was an error saving your learning circle. Please try again.'
          }
        })
      }

      const opts = { data, onSuccess, onError, onFail };
      const api = new ApiHelper('learningCircles');

      if (this.state.learningCircle.id) {
        api.updateResource(opts, this.state.learningCircle.id)
      } else {
        api.createResource(opts);
      }
    } else {
      this.showModal()
    }
  }

  _onCancel() {
    window.location.href = FACILITATOR_PAGE;
  }

  _onLogin(user) {
    this.setState({ user }, this.onSubmitForm)
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
          learningCircle={this.state.learningCircle}
          errors={this.state.errors}
          onCancel={this.onCancel}
          onSubmitForm={this.onSubmitForm}
        />
        <HelpContainer currentTab={this.state.currentTab} />
        <RegistrationModal
          open={this.state.showModal}
          closeModal={this.closeModal}
          user={this.props.user}
          onLogin={this.onLogin}
        />
      </div>
    );
  }
}
