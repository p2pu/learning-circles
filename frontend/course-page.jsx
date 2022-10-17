import React from 'react'
import ReactDOM from 'react-dom'
import CourseLearningCircles from './components/course-learning-circles'

/*
 * Add react component to page to display learning circles associated with the course
 */

const dataEl = document.getElementById('course-learning-circles-data');
const learningCircles = JSON.parse(dataEl.textContent);
const reactRoot = document.getElementById('course-learning-circles');

ReactDOM.render(
  <CourseLearningCircles 
    learningCircles={learningCircles}
    defaultImageUrl={reactRoot.dataset.defaultImageUrl}
  />,
  reactRoot
);
