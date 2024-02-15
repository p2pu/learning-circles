import React from 'react'
import ReactDOM from 'react-dom'
import CreateLearningCirclePage from './components/create-learning-circle-page'


const element = document.getElementById('create-learning-circle-form')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const userId = window.currentUserId;
const learningCircle = window.lc;
const tinymceScriptSrc = "/static/js/vendor/tinymce/tinymce.min.js";
const teamCourseList = window.teamCourseList;

ReactDOM.render(<CreateLearningCirclePage user={user} userId={userId} learningCircle={learningCircle} team={team} teamCourseList={teamCourseList} tinymceScriptSrc={tinymceScriptSrc} />, element)
