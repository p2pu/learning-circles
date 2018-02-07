import React from 'react'
import Search from './form_fields/Search'

import '../stylesheets/search.scss'

const CourseSection = (props) => {
  const scrollToTop = () => {
    document.querySelector('.form-container').scrollTop = 0;
  }

  return (
    <div>
      {
        props.errors.course &&
        <div className="error-message minicaps">{props.errors.course}</div>
      }
      {
        props.learningCircle.course &&
        <p>
          Selected course: <span className='course-title'>{props.learningCircle.courseTitle}</span><br />
          <a style={{cursor: 'pointer'}} onClick={() => props.updateFormData({ course: null })}>Remove selection</a>
        </p>
      }
      <Search
        learningCircle={props.learningCircle}
        searchSubject={'courses'}
        updateFormData={props.updateFormData}
        scrollToTop={scrollToTop}
        showHelp={props.showHelp}
      />
    </div>
  );
}


export default CourseSection