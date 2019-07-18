import React from 'react'
import axios from 'axios'

import Notification from './Notification'

const TeamInvitationNotification = ({ invitation }) => {
  return (
    <Notification level="warning" dismissable={true}>
      {
        invitation.team_organizer_name ?
        <p className="mb-0"><span className="bold">{invitation.team_organizer_name}</span> invited you to join <span className="bold">{invitation.team_name}</span>. Do you want to join this team?</p> :
        <p className="mb-0">Based on your email address, you've been invited to join <span className="bold">{invitation.team_name}</span>. Do you want to join this team?</p>
      }
      <a href={invitation.team_invitation_confirmation_url}>Respond to the invitation</a>
    </Notification>
  );
}

export default TeamInvitationNotification
