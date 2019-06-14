import React from 'react'
import axios from 'axios'

import Notification from './Notification'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class EmailValidationNotification extends React.Component {
  submitForm = e => {
    e.preventDefault()
    const url = this.props.emailConfirmationUrl;

    console.log(url)

    axios({
      url,
      method: 'POST',
      config: { headers: {'Content-Type': 'application/json' }}
    }).then(res => {
      if (res.status === 200) {
        this.props.showAlert("We've sent you a validation email, check your inbox!", "success")
      } else {
        this.props.showAlert("There was an error sending the validation email. Please contact us at thepeople@p2pu.org.", "warning")
      }
    }).catch(err => {
      this.props.showAlert("There was an error sending the validation email. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })
  }

  render() {
    return (
      <Notification level="warning" dismissable={true}>
        <p className="mb-0">Your email address has not yet been validated. Check your inbox for an email from us.</p>
        <a href="#" onClick={this.submitForm}>Re-send the validation email</a>
      </Notification>
    );
  }
}

export default EmailValidationNotification
