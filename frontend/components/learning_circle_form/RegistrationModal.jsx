import React from 'react';
import axios from 'axios';

import Modal from 'react-responsive-modal';
import CheckboxWithLabel from 'p2pu-input-fields/dist/CheckboxWithLabel'
import InputWithLabel from 'p2pu-input-fields/dist/InputWithLabel'

import { API_ENDPOINTS } from '../../helpers/constants'

import '../stylesheets/learning-circle-form.scss';
import 'p2pu-input-fields/dist/build.css';


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

export default class RegistrationModal extends React.Component {

  constructor(props) {
    super(props);
    this.state = { user: this.props.user || { communication_opt_in: true }, errors: {}, registration: true };
    this.updateUserData = (data) => this._updateUserData(data);
    this.toggleModalType = () => this._toggleModalType();
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

  _toggleModalType() {
    this.setState({ registration: !this.state.registration });
  }

  _submitForm(e) {
    e.preventDefault()
    const data = this.state.user;
    const url = this.state.registration ? API_ENDPOINTS.registration : API_ENDPOINTS.login;

    axios({
      url,
      data,
      method: 'post',
      responseType: 'json',
      config: { headers: {'Content-Type': 'application/json' }}
    }).then(res => {
      if (!!res.data.errors) {
        if (typeof(res.data.errors) == "string") {
          return this.props.showAlert(res.data.errors, 'danger');
        }
        return this.setState({ errors: res.data.errors });
      }
      this.props.closeModal();
      this.props.onLogin(res.data.user);
    }).catch(err => {
      console.log(err);
    })
  }

  render() {
    return (
      <Modal open={this.props.open} onClose={this.props.closeModal} classNames={{modal: 'registration-modal', overlay: 'modal-overlay'}}>
        <div className='registration-modal-content'>
          {
            this.state.registration &&
            <h4>Create an account</h4>
          }
          {
            !this.state.registration &&
            <h4>Log in</h4>
          }
          {
            this.state.registration &&
            <p>In order to save your learning circle, you need to register or <a onClick={this.toggleModalType}>log in.</a></p>
          }
          {
            !this.state.registration &&
            <p>In order to save your learning circle, you need to log in or <a onClick={this.toggleModalType}>register.</a></p>
          }
          <form id='registration-form' onSubmit={this.submitForm}>
            { this.state.registration &&
              <InputWithLabel
                label={'First name:'}
                value={this.state.user.first_name || ''}
                handleChange={this.updateUserData}
                name={'first_name'}
                id={'id_first_name'}
                type={'text'}
                errorMessage={this.state.errors.first_name}
              />
            }
            { this.state.registration &&
              <InputWithLabel
                label={'Last name:'}
                value={this.state.user.last_name || ''}
                handleChange={this.updateUserData}
                name={'last_name'}
                id={'id_last_name'}
                type={'text'}
                errorMessage={this.state.errors.last_name}
              />
            }
            <InputWithLabel
              label={'Email address:'}
              value={this.state.user.email || ''}
              handleChange={this.updateUserData}
              name={'email'}
              id={'id_email'}
              type={'email'}
              errorMessage={this.state.errors.email}
            />
            <InputWithLabel
              label={'Password:'}
              value={this.state.user.password || ''}
              handleChange={this.updateUserData}
              name={'password'}
              id={'id_password'}
              type={'password'}
              errorMessage={this.state.errors.password}
            />
            { this.state.registration &&
              <div>
                <p>Joining the community comes with an expectation that you would like to learn about upcoming events, new features, and updates from around the world. If you do not want to receive any of these messages, uncheck this box.</p>
                <CheckboxWithLabel
                  label='P2PU can contact me.'
                  checked={this.state.user.communication_opt_in}
                  handleChange={this.updateUserData}
                  name={'communication_opt_in'}
                  id={'id_communication_opt_in'}
                  errorMessage={this.state.errors.communication_opt_in}
                />
              </div>
            }
            <div className="modal-actions">
              <a onClick={this.toggleModalType}>
                { this.state.registration ? 'Already have an account? Log in here.' : 'Don\'t have an account? Register here.' }
              </a>
              <div className="buttons">
                <button className="p2pu-btn dark" onClick={(e) => {e.preventDefault(); this.props.closeModal()}}>Cancel</button>
                <button type='submit' className="p2pu-btn blue">{ this.state.registration ? 'Register' : 'Log in' }</button>
              </div>
            </div>
          </form>
        </div>
      </Modal>
    );
  }
}

