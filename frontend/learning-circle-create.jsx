import React from 'react'
import ReactDOM from 'react-dom'
import CreateLearningCirclePage from './components/create-learning-circle-page'


const element = document.getElementById('create-learning-circle-form')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const studygroup = element.dataset.studygroup

ReactDOM.render(<CreateLearningCirclePage user={user} studygroup={studygroup} />, element)