import React from 'react'
import ReactDOM from 'react-dom'
import DiscourseTopicPreview from './components/discourse-topic-preview'
import SimilarCoursesPreview from './components/similar-courses-preview'


const discussion = document.getElementById('course-discussion-preview')
const similarCourses = document.getElementById('similar-courses')
const courses = similarCourses.dataset.courses


ReactDOM.render(<DiscourseTopicPreview thread={"abc"} />, discussion)
ReactDOM.render(<SimilarCoursesPreview courses={courses} />, similarCourses)