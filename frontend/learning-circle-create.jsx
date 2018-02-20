import React from 'react'
import ReactDOM from 'react-dom'
import CreateLearningCirclePage from './components/create-learning-circle-page'


const element = document.getElementById('create-learning-circle-form')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const learningCircle = window.lc

ReactDOM.render(<CreateLearningCirclePage user={user} learningCircle={learningCircle} />, element)