import React from 'react'
import axios from 'axios'

import Notification from './Notification'

const TeamInvitationNotification = props => {
  return (
    <Notification level="warning" dismissable={true}>
      {
        props.teamOrganizerName ?
        <p className="mb-0"><span className="bold">{props.teamOrganizerName}</span> invited you to join <span className="bold">{props.teamName}</span>. Do you want to join this team?</p> :
        <p className="mb-0">Based on your email address, you've been invited to join <span className="bold">{props.teamName}</span>. Do you want to join this team?</p>
      }
      <a href={props.teamInvitationUrl}>Respond to the invitation</a>
    </Notification>
  );
}

export default TeamInvitationNotification
