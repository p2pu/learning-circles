import React from 'react';
import axios from 'axios';

import Modal from 'react-responsive-modal';
import InputWithLabel from './common/InputWithLabel'


import './stylesheets/learning-circle-form.scss'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default class RegistrationModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = { user: this.props.user || {} };
    this.updateUserData = (data) => this._updateUserData(data);
    this.submitForm = (e) => this._submitForm(e);
  }

  _updateUserData(data) {
    this.setState({
      user: {
        ...this.state.user,
        ...data
      }
    })
  }

  _submitForm(e) {
    e.preventDefault()
    const data = new FormData(e.currentTarget);
    const url = '/en/facilitator/signup/'

    axios({
      url,
      data,
      method: 'post',
      responseType: 'json',
      config: { headers: {'Content-Type': 'multipart/form-data' }}
    }).then(res => {
      console.log(res)
    }).catch(err => {
      console.log(err)
    })
  }

  render() {
    return (
      <Modal open={this.props.open} onClose={this.props.closeModal} classNames={{modal: 'registration-modal', overlay: 'modal-overlay'}} little>
        <div className='registration-modal-content'>
          <h4>Create an account</h4>
          <p>In order to save your learning circle, you need to register or <a href='/en/accounts/login/'>log in</a>.</p>
          <form id='registration-form' onSubmit={this.submitForm}>
            <InputWithLabel
              label={'First name:'}
              value={this.state.user.first_name || ''}
              handleChange={this.updateUserData}
              name={'first_name'}
              id={'id_first_name'}
              type={'text'}
            />
            <InputWithLabel
              label={'Last name:'}
              value={this.state.user.last_name || ''}
              handleChange={this.updateUserData}
              name={'last_name'}
              id={'id_last_name'}
              type={'text'}
            />
            <InputWithLabel
              label={'Email address:'}
              value={this.state.user.username || ''}
              handleChange={this.updateUserData}
              name={'username'}
              id={'id_username'}
              type={'email'}
            />
            <InputWithLabel
              label={'Password:'}
              value={this.state.user.password || ''}
              handleChange={this.updateUserData}
              name={'password'}
              id={'id_password'}
              type={'password'}
            />
            <div className="modal-actions">
              <a href='/en/accounts/login/'>Already have an account? Log in here.</a>
              <div className="buttons">
                <button className="p2pu-btn dark" onClick={(e) => {e.preventDefault(); this.props.closeModal()}}>Cancel</button>
                <button type='submit' className="p2pu-btn blue">Register</button>
              </div>
            </div>
          </form>
        </div>
      </Modal>
    );
  }
}

