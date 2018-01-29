import React from 'react';
import axios from 'axios';
import FormTabs from './form-tabs';
import HelpSection from './help-section';
import ActionBar from './action-bar';
import Modal from 'react-responsive-modal';
import InputWithLabel from './common/InputWithLabel'
import RegistrationModal from './registration-modal'

import { LC_PUBLISHED_PAGE, LC_SAVED_DRAFT_PAGE, API_ENDPOINTS, FACILITATOR_PAGE } from '../constants';


import './stylesheets/learning-circle-form.scss'

export default class CreateLearningCircleForm extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      currentTab: 0,
      showHelp: true,
      learningCircle: {},
      showModal: false,
      showHelp: false,
      user: this.props.user
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
      3: '4. Finalize'
    };
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
        window.location.href = LC_PUBLISHED_PAGE;
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
        window.location.href = LC_SAVED_DRAFT_PAGE;
      }).catch(err => {
        console.log(err)
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
        <div className='show-help' onClick={this.toggleHelp}>
          <i className="material-icons">{ this.state.showHelp ? 'close' : 'info_outline' }</i>
          <small className='minicaps'>{ this.state.showHelp ? 'back' : 'info' }</small>
        </div>
        <FormTabs
          updateFormData={this.updateFormData}
          showHelp={this.state.showHelp}
          toggleHelp={this.toggleHelp}
          currentTab={this.state.currentTab}
          allTabs={this.allTabs}
          changeTab={this.changeTab}
          learningCircle={this.state.learningCircle}
        />
        <HelpSection currentTab={this.state.currentTab} />
        <ActionBar
          currentTab={this.state.currentTab}
          changeTab={this.changeTab}
          onSaveDraft={this.onSaveDraft}
          onCancel={this.onCancel}
          onSubmitForm={this.onSubmitForm}
        />
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
