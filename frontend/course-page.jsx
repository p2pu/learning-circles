import React from 'react'
import ReactDOM from 'react-dom'
import DiscourseTopicPreview from './components/discourse-topic-preview'
import SimilarCoursesPreview from './components/similar-courses-preview'


const discussion = document.getElementById('course-discussion-preview')
const similarCourses = document.getElementById('similar-courses')
const courses = similarCourses.dataset.courses
const topicUrl = discussion.dataset.topicUrl;

ReactDOM.render(<DiscourseTopicPreview topicUrl={topicUrl} />, discussion)
ReactDOM.render(<SimilarCoursesPreview courses={courses} />, similarCourses)