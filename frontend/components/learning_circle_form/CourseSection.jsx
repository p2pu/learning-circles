import React from 'react'
//import { Search, BrowseCourses, CourseCard } from 'p2pu-components';

import SearchProvider from 'p2pu-components/dist/Search/SearchProvider'
import SearchCourses from 'p2pu-components/dist/Courses/SearchCourses'
import CourseCard from 'p2pu-components/dist/Courses/CourseCard'
import BrowseCourses from 'p2pu-components/dist/Courses/Browse'
import SearchAndFilter from 'p2pu-components/dist/Courses/SearchAndFilter'
import SearchSummary from 'p2pu-components/dist/Courses/SearchSummary'
import SearchBar from 'p2pu-components/dist/Search/SearchBar'

import OrderCoursesForm from 'p2pu-components/dist/Courses/OrderCoursesForm'
import TopicsFilterForm from 'p2pu-components/dist/Courses/TopicsFilterForm'
import LanguageFilterForm from 'p2pu-components/dist/Courses/LanguageFilterForm'
import OerFilterForm from 'p2pu-components/dist/Courses/OerFilterForm'
import FacilitatorGuideFilterForm from 'p2pu-components/dist/Courses/FacilitatorGuideFilterForm'


import 'p2pu-components/dist/build.css';


const CustomCourseSearch = (props) => {
    return (
      <>
        <SearchBar
          updateQueryParams={props.updateQueryParams}
          q={props.q}
        />

        <a data-bs-toggle="collapse" href="#searchFilters" role="button" aria-expanded="false" aria-controls="searchFilters">
          Advanced options <i className="fa fa-chevron-down"></i>
        </a>

        <div id="searchFilters" className="collapse">
          <div className="col-12">
            <OrderCoursesForm {...props} />
          </div>
          <div className="col-12">
            <TopicsFilterForm {...props} />
          </div>
          <div className="col-12">
            <LanguageFilterForm {...props} />
          </div>
          <div className="col-12">
            <FacilitatorGuideFilterForm {...props} />
          </div>
          <div className="col-12">
            <OerFilterForm {...props} />
          </div>
        </div>

        <SearchSummary {...props} />
        <BrowseCourses {...props} />
      </>
    );
}


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
          <SearchProvider
            columnBreakpoints={props.showHelp ? 1 : 3}
            searchSubject={'courses'}
            initialState={{languages: ['en']}}
            onSelectResult={handleSelectResult}
            origin={window.location.origin}
            scrollContainer={'.tabs-container'}
            NoResultsComponent={() => <p className="my-4">{`There are no matching courses.`}<a className="btn p2pu-btn btn-secondary" href={`${window.location.origin}${window.location.pathname}`}>Start over</a></p>}
          >
            <CustomCourseSearch/>
          </SearchProvider>
        }
    </div>
  );
}


export default CourseSection
