import React from 'react'
import ReactDOM from 'react-dom'
import FacilitatorDashboard from './components/dashboard/FacilitatorDashboard'


const element = document.getElementById('facilitator-dashboard')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;

ReactDOM.render(<FacilitatorDashboard user={user} />, element)