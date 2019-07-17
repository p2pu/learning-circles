import React, { Component } from "react";
import InputWithLabel from 'p2pu-input-fields/dist/InputWithLabel'
import axios from "axios"

export default class OrganizerTeamInvitations extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      inviteError: null,
      teamInvitationUrl: this.props.teamInvitationUrl,
    };
  }

  handleEmailInputChange = value => {
    this.setState({ email: value.email })
  }

  handleInviteSubmit = e => {
    e.preventDefault();
    this.setState({inviteError: null});
    const url = this.props.teamMemberInvitationUrl;

    axios({
      url,
      method: 'POST',
      data: { email: this.state.email },
      config: { headers: {'Content-Type': 'application/json' }}
    }).then(res => {
      console.log(res)
      if (res.status === 200) {
        if (res.data.status === "CREATED") {
          this.props.showAlert(`We've sent a team invitation to ${this.state.email}.`, "success")
          this.setState({ email: "", inviteError: null })
        } else if (res.data.status === "ERROR") {
          this.setState({ inviteError: res.data.errors._ })
        }
      } else {
        this.props.showAlert("There was an error sending the team invitation. Please contact us at thepeople@p2pu.org.", "warning")
      }
    }).catch(err => {
      this.props.showAlert("There was an error sending the team invitation. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })
  }

  handleCreateUrl = () => {
    axios({
      url: this.props.createTeamInvitationUrl,
      method: 'POST',
    }).then(res => {
      console.log(res)
      if (res.status === 200 && res.data.status === "updated") {
        this.setState({ teamInvitationUrl: res.data.team_invitation_url })
      } else {
        this.props.showAlert("There was an error creating the URL. Please contact us at thepeople@p2pu.org.", "warning")
      }
    }).catch(err => {
      this.props.showAlert("There was an error creating the URL. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })
  }

  handleDeleteUrl = () => {
    axios({
      url: this.props.deleteTeamInvitationUrl,
      method: 'POST',
    }).then(res => {
      console.log(res)
      if (res.status === 200 && res.data.status === "deleted") {
        this.setState({ teamInvitationUrl: res.data.team_invitation_url })
      } else {
        this.props.showAlert("There was an error deleting the URL. Please contact us at thepeople@p2pu.org.", "warning")
      }
    }).catch(err => {
      this.props.showAlert("There was an error deleting the URL. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })
  }

  render() {
    return (
      <div className="mt-3">
        <div className="invitation-form">
          <div className="card-title">Send an Invitation</div>
          <form className="form-group" onSubmit={this.handleInviteSubmit}>
            <InputWithLabel
              label={'Email address of person to invite'}
              type="email"
              value={this.state.email}
              handleChange={this.handleEmailInputChange}
              name={'email'}
              id={'id_email'}
              errorMessage={this.state.inviteError}
            />
            <input type="button" className="p2pu-btn dark btn-sm" type="submit" value="Send Invitation" />
          </form>
        </div>

        <div className="invitation-link">
          <div className="card-title">Invitation Link</div>
          <p>Anyone with this URL will be able to join your team without an invitation. Share at your discretion!</p>
          { this.state.teamInvitationUrl && <p><code className="copy-url">{this.state.teamInvitationUrl}</code></p> }
          <div>
            <button onClick={this.handleCreateUrl} className="p2pu-btn dark btn-sm">Generate new URL</button>
            { this.state.teamInvitationUrl &&
              <button onClick={this.handleDeleteUrl} className="p2pu-btn dark secondary btn-sm">Delete URL</button>
            }
          </div>
        </div>
      </div>
    );
  }
}
