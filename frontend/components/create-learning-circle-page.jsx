import React from 'react';
import axios from 'axios';
import FormContainer from './learning_circle_form/FormContainer';
import HelpContainer from './learning_circle_form/HelpContainer';
import RegistrationModal from './registration-modal';
import Alert from './Alert';
import ApiHelper from '../helpers/ApiHelper'

import { LC_PUBLISHED_PAGE, LC_SAVED_DRAFT_PAGE, API_ENDPOINTS, FACILITATOR_PAGE } from '../constants';


import './stylesheets/learning-circle-form.scss'

export default class CreateLearningCirclePage extends React.Component {

  constructor(props){
    super(props);
    const desktop = window.screen.width > 768;
    this.state = {
      currentTab: 0,
      learningCircle: {},
      showModal: false,
      showHelp: desktop,
      user: this.props.user,
      errors: {},
      alert: { show: false }
    };
    this.changeTab = (tab) => this._changeTab(tab);
    this.onSubmitForm = () => this._onSubmitForm();
    this.onCancel = () => this._onCancel();
    this.onSaveDraft = () => this._onSaveDraft();
    this.toggleHelp = () => this._toggleHelp();
    this.showModal = () => this._showModal();
    this.closeModal = () => this._closeModal();
    this.updateFormData = (data) => this._updateFormData(data);
    this.updateUserData = (data) => this._updateUserData(data);
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
    window.addEventListener('beforeunload', (e) => {
      if (!!Object.keys(this.state.learningCircle).length) {
        const dialogText = 'You have unsaved data on this page. Are you sure you want to leave?'
        e.returnValue = dialogText;
        return dialogText;
      }
    });

    const urlParams = new URL(window.location.href).searchParams;
    const courseId = urlParams.get('course_id');
    if (!!courseId) {
      const api = new ApiHelper('courses');
      const params = { course_id: courseId }
      const callback = (response, _opts) => {
        this.setState({ learningCircle: { course: response.items[0] } })
      }
      const opts = { params, callback }

      api.fetchResource(opts)
    }
    this.setState({ learningCircle: { course: { id: urlParams.get('course_id') }}})
  }

  _updateFormData(data) {
    this.setState({
      learningCircle: {
        ...this.state.learningCircle,
        ...data
      }
    })
  }

  _toggleHelp() {
    this.setState({ showHelp: !this.state.showHelp })
  }

  _changeTab(tab) {
    if (!!this.allTabs[tab]) {
      this.setState({ currentTab: tab })
    } else {
      this.setState({ currentTab: 0 })
    }
  }

  _showModal() {
    this.setState({ showModal: true })
  }

  _closeModal() {
    this.setState({ showModal: false })
  }

  _onSubmitForm() {
    if (this.state.user) {
      const data = this.state.learningCircle;
      const url = API_ENDPOINTS.learningCircle;

      axios({
        url,
        data,
        method: 'post',
        responseType: 'json',
        config: { headers: {'Content-Type': 'application/json' }}
      }).then(res => {
        if (res.data.status === 'created') {
          window.location.href = `${LC_PUBLISHED_PAGE}?url=${res.data.study_group_url}`;
        } else if (res.data.errors) {
          this.setState({ errors: res.data.errors, currentTab: 0 })
        }
      }).catch(err => {
        console.log(err)
      })

    } else {
      this.showModal()
    }
  }

  _onCancel() {
    this.setState({ learningCircle: null })
    window.location.href = FACILITATOR_PAGE;
  }

  _onSaveDraft() {
    if (this.state.user) {
      const data = this.state.learningCircle
      const url = API_ENDPOINTS.learningCircle;

      axios({
        url,
        data,
        method: 'post',
        responseType: 'json',
        config: { headers: {'Content-Type': 'application/json' }}
      }).then(res => {
        console.log(res)
        if (res.data.status === 'created') {
          window.location.href = LC_SAVED_DRAFT_PAGE;
        } else if (res.data.status === 'error') {
          this.setState({
            errors: res.data.errors,
            alert: {
              show: true,
              type: 'danger',
              message: 'There was a problem saving your learning circle. Please check the error messages in the form and make the necessary changes.'
            }
          })
        }
      }).catch(err => {
        console.log(err)
        this.setState({
          alert: {
            show: true,
            type: 'danger',
            message: 'There was an error saving your learning circle. Please try again.'
          }
        })
      })

    } else {
      this.showModal()
    }
  }

  _onLogin(user, callback=null) {
    this.setState({ user }, callback)
  }

  render() {
    return (
      <div className='page-container'>
        <Alert show={this.state.alert.show} type={this.state.alert.type}>
          {this.state.alert.message}
        </Alert>
        <div className='help-toggle' onClick={this.toggleHelp}>
          <i className="material-icons">{ this.state.showHelp ? 'close' : 'info_outline' }</i>
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
          onSaveDraft={this.onSaveDraft}
          onCancel={this.onCancel}
          onSubmitForm={this.onSubmitForm}
        />
        <HelpContainer currentTab={this.state.currentTab} />
        <RegistrationModal
          open={this.state.showModal}
          closeModal={this.closeModal}
          user={this.props.user}
          onLogin={this.onLogin}
          onSaveDraft={this.onSaveDraft}
        />
      </div>
    );
  }
}
