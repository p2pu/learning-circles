import React from 'react'
import ReactDOM from 'react-dom'
import DiscourseTopicPreview from './components/discourse-topic-preview'
import SimilarCoursesPreview from './components/similar-courses-preview'
import CourseLearningCircles from './components/course-learning-circles'

const learningCircles = document.getElementById('course-learning-circles-data');
reactDOM.render(<CourseLearningCircles learningCircles={learningCircles} />, document.getElementById('course-learning-circles'));
