import React from 'react'
import axios from 'axios'

import Notification from './Notification'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

class ImplicitTeamInvitationNotification extends React.Component {
  state = { notificationDismissed: false }

  submitForm = response => e => {
    e.preventDefault()
    const url = this.props.implicitTeamInvitationUrl;
    let formData = new FormData();
    formData.set('response', response);

    axios({
      url,
      method: 'POST',
      config: { headers: {'Content-Type': 'multipart/form-data' }},
      data: formData
    }).then(res => {
      if (res.status === 200) {
        if (response === "yes") {
          this.props.showAlert(`Welcome to the team! You are now a member of ${this.props.teamName}.`, "success")
        } else {
          this.props.showAlert("Thanks for your response.", "info")
        }
        this.setState({ notificationDismissed: true })
      } else {
        console.log(res)
        this.props.showAlert("There was an error adding you to the team. Please contact us at thepeople@p2pu.org.", "warning")
      }
    }).catch(err => {
      this.props.showAlert("There was an error adding you to the team. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })
  }

  render() {
    return (
      <Notification level="warning" dismissable={true} dismissed={this.state.notificationDismissed}>
        <p className="mb-0">Based on your email address, you've been invited to join <span className="bold">{this.props.teamName}</span>. Do you want to join this team?</p>
        <a href="#" onClick={this.submitForm("yes")} className="mr-2">Yes</a>
        <a href="#" onClick={this.submitForm("no")}>No</a>
      </Notification>
    );
  }
}

export default ImplicitTeamInvitationNotification
