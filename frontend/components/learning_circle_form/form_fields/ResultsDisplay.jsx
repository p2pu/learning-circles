import React from 'react'
import BrowseCourses from './BrowseCourses'
import SearchTags from './SearchTags'

const ResultsDisplay = (props) => {
  const resetSearch = () => { window.location.reload() };

  return(
    <div className="search-results col-sm-12">
      <SearchTags {...props} />
      <BrowseCourses
        courses={props.searchResults}
        updateFormData={props.updateFormData}
        updateQueryParams={props.updateQueryParams}
      />
    </div>
  )
}

export default ResultsDisplay