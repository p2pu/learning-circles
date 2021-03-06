import React from 'react'
import { Search, BrowseCourses, CourseCard } from 'p2pu-components';

import 'p2pu-components/dist/build.css';


const CourseSection = (props) => {
  const removeCourseSelection = () => {
    props.updateFormData({ course: {} });
    const cleanUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, cleanUrl)
  }

  const scrollToTop = () => document.querySelector('body').scrollTop = 0;

  const handleSelectResult = selected => {
    props.updateFormData({ course: selected })
    scrollToTop()
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
            columnBreakpoints={props.showHelp ? 1 : 3}
            searchSubject={'courses'}
            initialState={{languages: ['en']}}
            Browse={BrowseCourses}
            onSelectResult={handleSelectResult}
            origin={window.location.origin}
            scrollContainer={'.tabs-container'}
            NoResultsComponent={() => <p className="my-4">{`There are no matching courses.`}<a className="btn p2pu-btn btn-secondary" href={`${window.location.origin}${window.location.pathname}`}>Start over</a></p>}
          />
        }
    </div>
  );
}


export default CourseSection
