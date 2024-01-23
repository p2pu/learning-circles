import React from 'react'
import ReactDOM from 'react-dom'
import ErrorBoundary from './components/error-boundary'

import SearchProvider from 'p2pu-components/dist/Search/SearchProvider'
import SearchCourses from 'p2pu-components/dist/Courses/SearchCourses'
import CourseCard from 'p2pu-components/dist/Courses/CourseCard'
//import BrowseCourses from 'p2pu-components/dist/Courses/Browse'
import SearchAndFilter from 'p2pu-components/dist/Courses/SearchAndFilter'
import SearchSummary from 'p2pu-components/dist/Courses/SearchSummary'
import SearchBar from 'p2pu-components/dist/Search/SearchBar'

import OrderCoursesForm from 'p2pu-components/dist/Courses/OrderCoursesForm'
import TopicsFilterForm from 'p2pu-components/dist/Courses/TopicsFilterForm'
import LanguageFilterForm from 'p2pu-components/dist/Courses/LanguageFilterForm'
import OerFilterForm from 'p2pu-components/dist/Courses/OerFilterForm'
import FacilitatorGuideFilterForm from 'p2pu-components/dist/Courses/FacilitatorGuideFilterForm'

import { t } from 'ttag';



const element = document.getElementById('team-courses')

const user = element.dataset.user === "AnonymousUser" ? null : element.dataset.user;
const teamId = element.dataset.teamId === "None" ? null : element.dataset.teamId;
const teamName = element.dataset.teamName === "None" ? null : element.dataset.teamName;
const userIsOrganizer = element.dataset.userIsOrganizer === "None" ? null : element.dataset.userIsOrganizer;


const BrowseCourses = props => {
  const { results, updateQueryParams, onSelectResult, columnBreakpoints, isLoading } = props;

  if (isLoading){
    return <></>;
  }

  return (
    <div className="search-results">
      {
        results.map((course, index) => (
          <CourseCard
            key={`course-card-${index}`}
            id={`course-card-${index}`}
            course={course}
            updateQueryParams={updateQueryParams}
            courseLink={props.courseLink}
            moreInfo={props.moreInfo}
            onSelectResult={onSelectResult}
            buttonText={t`Add this course`}
            classes="mb-4"
          />
        ))
      }
    </div>
  );
}

// TODO dedup with frontend/components/learning_circle_form/CourseSelection.jsx
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
      <BrowseCourses {...props} onSelectResult={ e=> console.log(e) }/>
    </>
  );
}


const TeamCourseSelection = props => {

  const handleSelectResult = selected => {
    props.updateFormData({ course: selected })
    scrollToTop()
  }

  return ( 
    <div id="team-course-selection">
      <h1>Select team courses</h1>
      <SearchProvider
        columnBreakpoints={props.showHelp ? 1 : 3}
        searchSubject={'courses'}
        initialState={{languages: ['en']}}
        onSelectResult={handleSelectResult}
        origin={window.location.origin}
        scrollContainer={'#team-course-selection'}
        NoResultsComponent={() => <p className="my-4">{`There are no matching courses.`}<a className="btn p2pu-btn btn-secondary" href={`${window.location.origin}${window.location.pathname}`}>Start over</a></p>}
      >
        <CustomCourseSearch/>
      </SearchProvider>
    </div>
  );
}

ReactDOM.render(
  <ErrorBoundary scope="team-courses">
    <TeamCourseSelection
      user={user}
      teamId={teamId}
      teamName={teamName}
      userIsOrganizer={userIsOrganizer}
      isMemberTeam={element.dataset.isMemberTeam}
      isStaff={element.dataset.isStaff}
    />
  </ErrorBoundary>,
  element
)
