import React from 'react'
import ReactDOM from 'react-dom'
import FacilitatorDashboard from './components/dashboard/FacilitatorDashboard'


const element = document.getElementById('facilitator-dashboard')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const teamName = element.dataset.teamName === "None" ? null : element.dataset.teamName;
const teamOrganizerName = element.dataset.teamOrganizerName === "None" ? null : element.dataset.teamOrganizerName;
const explicitTeamInvitationUrl = element.dataset.explicitTeamInvitationUrl === "None" ? null : element.dataset.explicitTeamInvitationUrl;
const implicitTeamInvitationUrl = element.dataset.implicitTeamInvitationUrl === "None" ? null : element.dataset.implicitTeamInvitationUrl;
const emailConfirmationUrl = element.dataset.emailConfirmationUrl === "None" ? null : element.dataset.emailConfirmationUrl;

ReactDOM.render(
  <FacilitatorDashboard
    user={user}
    teamName={teamName}
    teamOrganizerName={teamOrganizerName}
    explicitTeamInvitationUrl={explicitTeamInvitationUrl}
    implicitTeamInvitationUrl={implicitTeamInvitationUrl}
    emailConfirmationUrl={emailConfirmationUrl}
  />, element)