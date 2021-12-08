import React, { Component } from "react";
import { InputWithLabel } from 'p2pu-components'
import axios from "axios"

export default class OrganizerTeamInvitations extends Component {
  constructor(props) {
    super(props);
    this.state = {
      email: "",
      inviteError: null,
      teamInvitationLink: this.props.teamInvitationLink,
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
      url: this.props.createTeamInvitationLink,
      method: 'POST',
    }).then(res => {
      console.log(res)
      if (res.status === 200 && res.data.status === "updated") {
        this.setState({ teamInvitationLink: res.data.team_invitation_link })
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
      url: this.props.deleteTeamInvitationLink,
      method: 'POST',
    }).then(res => {
      console.log(res)
      if (res.status === 200 && res.data.status === "deleted") {
        this.setState({ teamInvitationLink: res.data.team_invitation_link })
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
            <input type="button" className="p2pu-btn dark btn btn-sm" type="submit" value="Send Invitation" />
          </form>
        </div>

        <div className="invitation-link">
          <div className="card-title">Invitation Link</div>
          <p>Anyone with this URL will be able to join your team without an invitation. Share at your discretion!</p>
          { this.state.teamInvitationLink && <p><code className="copy-url">{this.state.teamInvitationLink}</code></p> }
          <div>
            <button onClick={this.handleCreateUrl} className="p2pu-btn btn dark btn-sm">Generate new URL</button>
            { this.state.teamInvitationLink &&
              <button onClick={this.handleDeleteUrl} className="p2pu-btn dark btn secondary btn-sm">Delete URL</button>
            }
          </div>
        </div>
      </div>
    );
  }
}
