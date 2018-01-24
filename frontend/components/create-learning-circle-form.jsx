import React from 'react';
import FormTabs from './form-tabs';
import HelpSection from './help-section';
import ActionBar from './action-bar';
import Modal from 'react-responsive-modal';
import InputWithLabel from './common/InputWithLabel'
import RegistrationModal from './registration-modal'


import './stylesheets/learning-circle-form.scss'

export default class CreateLearningCircleForm extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      currentTab: 0,
      showHelp: true,
      learningCircle: {},
      user: {},
      showModal: false
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
    }, () => console.log(this.state.learningCircle))
  }

  _updateUserData(data) {
    this.setState({
      user: {
        ...this.state.user,
        ...data
      }
    }, () => console.log(this.state.user))
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
    if (this.props.user) {
      console.log(this.state.learningCircle)
      // save learning circle
    } else {
      this.showModal()
    }
  }

  _onCancel() {
    this.setState({ learningCircle: null })
    window.location.href = '/en/facilitator'
  }

  _onSaveDraft() {
    if (this.props.user) {
      console.log(this.state.learningCircle)
      // save learning circle
    } else {
      this.showModal()
    }
  }

  _registerUser() {
    let userFormData = new FormData();
    userFormData.append('username', this.state.user.username)
    userFormData.append('first_name', this.state.user.first_name)
    userFormData.append('last_name', this.state.user.last_name)
    userFormData.append('password', this.state.user.password)
    userFormData.append('csrfmiddlewaretoken', this.props.token)

    const url = '/en/facilitator/signup/'

    const request = new XMLHttpRequest();
    request.open("POST", url);
    request.send(userFormData);
  }

  render() {
    return (
      <div className='page-container'>
        <FormTabs
          updateFormData={this.updateFormData}
          showHelp={this.state.showHelp}
          toggleHelp={this.toggleHelp}
          currentTab={this.state.currentTab}
          allTabs={this.allTabs}
          changeTab={this.changeTab}
          learningCircle={this.state.learningCircle}
        />
        <HelpSection currentTab={this.state.currentTab} open={this.state.openHelp} />
        <ActionBar
          currentTab={this.state.currentTab}
          changeTab={this.changeTab}
          onSaveDraft={this.onSaveDraft}
          onCancel={this.onCancel}
          onSubmitForm={this.onSubmitForm}
        />
        <RegistrationModal
          updateUserData={this.updateUserData}
          open={this.state.showModal}
          closeModal={this.closeModal}
          user={this.state.user}
          registerUser={this.registerUser}
        />
      </div>
    );
  }
}
