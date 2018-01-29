import React from 'react'
import ReactDOM from 'react-dom'
import CreateLearningCircleForm from './components/create-learning-circle-form'


const element = document.getElementById('create-learning-circle-form')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;

ReactDOM.render(<CreateLearningCircleForm user={user} />, element)