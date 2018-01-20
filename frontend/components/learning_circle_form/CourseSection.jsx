import React from 'react'
import Search from './form_fields/Search'

import '../stylesheets/search.scss'

const CourseSection = (props) => {
  return (
    <div>
      <p>Select a course below or <a href='#'>add a course</a></p>
      <Search searchSubject={'courses'} updateFormData={props.updateFormData} />
    </div>
  );
}


export default CourseSection