import React from 'react'
import ReactDOM from 'react-dom'
import FacilitatorDashboard from './components/dashboard/FacilitatorDashboard'


const element = document.getElementById('facilitator-dashboard')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const teamName = element.dataset.teamName === "None" ? null : element.dataset.teamName;
const teamInvitationUrl = element.dataset.teamInvitationUrl === "None" ? null : element.dataset.teamInvitationUrl;
const emailConfirmationUrl = element.dataset.emailConfirmationUrl === "None" ? null : element.dataset.emailConfirmationUrl;


ReactDOM.render(
  <FacilitatorDashboard
    user={user}
    teamName={teamName}
    teamInvitationUrl={teamInvitationUrl}
    emailConfirmationUrl={emailConfirmationUrl}
  />, element)