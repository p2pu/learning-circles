import React from 'react'
import ReactDOM from 'react-dom'
import OrganizerDash from './components/organizer-dash'

ReactDOM.render(
    <OrganizerDash
        teamInviteUrl={window.organizerDash.teamInviteUrl}
        activeLearningCircles={window.organizerDash.activeLearningCircle}
        facilitators={window.organizerDash.facilitators}
        meetings={window.organizerDash.meetings}
        invitations={window.organizerDash.invitations}/>, 
    document.getElementById('organizer-dash')
);
