import React from 'react';

import Modal from 'react-responsive-modal';
import InputWithLabel from './common/InputWithLabel'


import './stylesheets/learning-circle-form.scss'

const RegistrationModal = (props) => {

    return (
      <Modal open={props.open} onClose={props.closeModal} classNames={{modal: 'registration-modal', overlay: 'modal-overlay'}} little>
        <div className='registration-modal-content'>
          <h4>Create an account</h4>
          <p>In order to save your learning circle, you need to register or <a href='/en/accounts/login/'>log in</a>.</p>
          <InputWithLabel
            label={'First name:'}
            value={props.user.first_name || ''}
            handleChange={props.updateUserData}
            name={'first_name'}
            id={'id_first_name'}
            type={'text'}
          />
          <InputWithLabel
            label={'Last name:'}
            value={props.user.last_name || ''}
            handleChange={props.updateUserData}
            name={'last_name'}
            id={'id_last_name'}
            type={'text'}
          />
          <InputWithLabel
            label={'Email address:'}
            value={props.user.username || ''}
            handleChange={props.updateUserData}
            name={'username'}
            id={'id_username'}
            type={'email'}
          />
          <InputWithLabel
            label={'Password:'}
            value={props.user.password || ''}
            handleChange={props.updateUserData}
            name={'password'}
            id={'id_password'}
            type={'password'}
          />
          <div className="modal-actions">
            <a href='/en/accounts/login/'>Already have an account? Log in here.</a>
            <div className="buttons">
              <button className="p2pu-btn dark">Cancel</button>
              <button className="p2pu-btn blue" onClick={props.registerUser}>Register</button>
            </div>
          </div>
        </div>
      </Modal>
    );
}

export default RegistrationModal;
