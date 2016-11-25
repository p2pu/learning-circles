import React from 'react'
import ReactDOM from 'react-dom'
import FacilitatorList from './components/facilitator-list'

ReactDOM.render(
    <FacilitatorList facilitators={window.organizer_dash.facilitators} />, 
    document.getElementById('organizer-dash-facilitators')
);
