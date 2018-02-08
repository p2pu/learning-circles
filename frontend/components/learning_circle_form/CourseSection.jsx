import React from 'react'
import Search from './course_search/Search'
import CourseCard from './course_search/CourseCard'

import '../stylesheets/search.scss'


const CourseSection = (props) => {
  const scrollToTop = () => {
    document.querySelector('.form-container').scrollTop = 0;
  }

  const removeCourseSelection = () => {
    props.updateFormData({ course: {} });
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl)
  }

  return (
    <div>
      {
        props.errors.course &&
        <div className="error-message minicaps">{props.errors.course}</div>
      }
      {
          props.learningCircle.course.id &&
          <div className="search-results">
            <p className="bold">Selected course:</p>
            <CourseCard
              course={props.learningCircle.course}
            />
            <a style={{cursor: 'pointer'}} onClick={removeCourseSelection}>Remove selection</a>
          </div>
        }
        {
          !props.learningCircle.course.id &&
          <Search
            learningCircle={props.learningCircle}
            searchSubject={'courses'}
            updateFormData={props.updateFormData}
            scrollToTop={scrollToTop}
            changeTab={props.changeTab}
            showHelp={props.showHelp}
          />
        }
    </div>
  );
}


export default CourseSection