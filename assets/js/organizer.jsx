import React from 'react'
import ReactDOM from 'react-dom'
import OrganizerDash from './components/organizer-dash'

ReactDOM.render(
    <OrganizerDash
        activeLearningCircles={window.organizerDash.activeLearningCircle}
        facilitators={window.organizerDash.facilitators}
        meetings={window.organizerDash.meetings} />, 
    document.getElementById('organizer-dash')
);
