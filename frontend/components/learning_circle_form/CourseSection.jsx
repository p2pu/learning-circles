import React from 'react'
import Search from './form_fields/Search'

import '../stylesheets/search.scss'

const CourseSection = (props) => {
  return (
    <div>
      {
        props.errors.course &&
        <div className="error-message minicaps">{props.errors.course}</div>
      }
      {
        props.learningCircle.course ?
        <p>Selected course: <span className='course-title'>{props.learningCircle.courseTitle}</span></p> :
        <p>Select a course below or <a href='/en/course/create/'>add a course</a></p>
      }
      <Search searchSubject={'courses'} updateFormData={props.updateFormData} />
    </div>
  );
}


export default CourseSection