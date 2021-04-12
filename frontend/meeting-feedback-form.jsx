import React from 'react'
import ReactDOM from 'react-dom'

import CreateLearningCirclePage from './components/create-learning-circle-page'
import MeetingFeedback from './components/meeting-feedback'

const elements = document.getElementsByClassName('meeting-feedback-form');

elements.forEach( element => {
  ReactDOM.render(<MeetingFeedback {...element.dataset} />, element)
})



