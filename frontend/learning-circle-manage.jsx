import React from 'react'
import ReactDOM from 'react-dom'

import MeetingFeedback from './components/meeting-feedback'
import LearningCircleFeedback from './components/learning-circle-feedback'

// Replace feedback form for earch meeting
const elements = document.getElementsByClassName('meeting-feedback');
for (let el of elements){
  ReactDOM.render(<MeetingFeedback {...el.dataset} />, el);
}

// Replace feedback form for learning circle
const element = document.getElementById('learning-circle-feedback');
if (element) {
  ReactDOM.render(<LearningCircleFeedback {...element.dataset} />, element);
}
