import React from 'react'
import ReactDOM from 'react-dom'

import MeetingFeedback from './components/meeting-feedback'
import LearningCircleFeedbackForm from './components/learning-circle-feedback-form'
import CourseFeedbackForm from './components/course-feedback-form'

import 'components/stylesheets/learning-circle-feedback.scss'

// Replace feedback form for earch meeting
const elements = document.getElementsByClassName('meeting-feedback-form');
for (let el of elements){
  ReactDOM.render(<MeetingFeedback {...el.dataset} />, el);
}

// Replace feedback form for learning circle
const element = document.getElementById('learning-circle-feedback-form');
if (element) {
  ReactDOM.render(<LearningCircleFeedbackForm {...element.dataset} />, element);
}

let courseFeedbackDiv = document.getElementById('course-feedback-form');
ReactDOM.render(
  <CourseFeedbackForm {...courseFeedbackDiv.dataset} />,
  courseFeedbackDiv
);
