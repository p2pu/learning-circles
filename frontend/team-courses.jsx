import React, {useState} from 'react'
import ReactDOM from 'react-dom'

import ErrorBoundary from './components/error-boundary'

import SearchProvider from 'p2pu-components/dist/Search/SearchProvider'
import CourseCard from 'p2pu-components/dist/Courses/CourseCard'
import SearchSummary from 'p2pu-components/dist/Courses/SearchSummary'
import SearchBar from 'p2pu-components/dist/Search/SearchBar'
import OrderCoursesForm from 'p2pu-components/dist/Courses/OrderCoursesForm'
import TopicsFilterForm from 'p2pu-components/dist/Courses/TopicsFilterForm'
import LanguageFilterForm from 'p2pu-components/dist/Courses/LanguageFilterForm'
import OerFilterForm from 'p2pu-components/dist/Courses/OerFilterForm'
import FacilitatorGuideFilterForm from 'p2pu-components/dist/Courses/FacilitatorGuideFilterForm'

import { t } from 'ttag';
import axios from "axios"

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


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
            buttonText={props.teamCourseIds.indexOf(course.id)==-1?t`Add this course`:'Remove this course'}
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
      <BrowseCourses {...props} />
    </>
  );
}


const TeamCourseSelection = props => {

  const {teamCourseIds: initialTeamCourseIds = []} = props;

  const [teamCourseIds, setTeamCourseIds] = useState(initialTeamCourseIds);
  const [selectionError, setSelectionError] = useState('');
  const [isPosting, setIsPosting] = useState(false);

  const handleSelectResult = selected => {
    // add course to team list and update state with team courses
    console.log(selected)

    const updatedCourseIds = teamCourseIds.indexOf(selected.id) !== -1 ? teamCourseIds.filter( c => c !== selected.id ) : teamCourseIds.concat(selected.id);

    setIsPosting(true);
    const url = props.courseListApiUrl;
    axios({
      url,
      method: 'PATCH',
      data: { courses: updatedCourseIds },
      config: { headers: {'Content-Type': 'application/json' }}
    }).then(res => {
      setIsPosting(false);
      console.log(res)
      if (res.status === 200) {
        //this.props.showAlert(`The course was added!`, "success")
        //this.setState({ email: "", inviteError: null })
        setTeamCourseIds(updatedCourseIds)
        setSelectionError('');
      } else {
        setSelectionError("There was an error updating the course list. Please contact us at thepeople@p2pu.org if the problem persists.")
      }
    }).catch(err => {
      setIsPosting(false);
      setSelectionError("There was an error updating the course list. Please contact us at thepeople@p2pu.org if the problem persists.")
      console.log(err);
    })

  }

  return ( 
    <div id="team-course-selection">
      { 
        Boolean(selectionError) &&
        <div class="alert alert-danger" role="alert">{selectionError}</div>
      }
      <h1>Select team courses</h1>
      <SearchProvider
        searchSubject={'courses'}
        initialState={{languages: ['en']}}
        onSelectResult={handleSelectResult}
        origin={window.location.origin}
        scrollContainer={'#team-course-selection'}
        NoResultsComponent={() => <p className="my-4">{`There are no matching courses.`}<a className="btn p2pu-btn btn-secondary" href={`${window.location.origin}${window.location.pathname}`}>Start over</a></p>}
      >
        <CustomCourseSearch
            teamCourseIds={teamCourseIds}
        />
      </SearchProvider>
      <div 
        style={
          {
            position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(255,255,255,0.9)',
            display: 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'text-align': 'center',
          }
        }
        className={isPosting?'visible':'invisible'}
      >
        <div>
          <span className="spinner-border spinner-border-sm" role="status"></span>&nbsp;
          <span>Submitting data</span>
        </div>
      </div>
    </div>
  );
}

function render(){
  const element = document.getElementById('team-courses')

  const {
    courseListApiUrl,
    isMemberTeam,
    isStaff,
  } = element.dataset;

  const props = {
    user: element.dataset.user === "AnonymousUser" ? null : element.dataset.user,
    teamId: element.dataset.teamId === "None" ? null : element.dataset.teamId,
    teamName: element.dataset.teamName === "None" ? null : element.dataset.teamName,
    userIsOrganizer: element.dataset.userIsOrganizer === "None" ? null : element.dataset.userIsOrganizer,
    teamCourseIds: element.dataset.teamCourseIds === "None" ? [] : JSON.parse(element.dataset.teamCourseIds),
    courseListApiUrl,
    isMemberTeam,
    isStaff,
  }

  ReactDOM.render(
    <ErrorBoundary scope="team-courses">
      <TeamCourseSelection {...props} />
    </ErrorBoundary>,
    element
  )
}
render();
