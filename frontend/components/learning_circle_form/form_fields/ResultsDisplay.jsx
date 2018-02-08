import React from 'react'
import BrowseCourses from './BrowseCourses'
import SearchTags from './SearchTags'

const ResultsDisplay = (props) => {
  return(
    <div className="search-results col-sm-12">
      <SearchTags {...props} />
      <BrowseCourses
        courses={props.searchResults}
        updateFormData={props.updateFormData}
        updateQueryParams={props.updateQueryParams}
        scrollToTop={props.scrollToTop}
        showHelp={props.showHelp}
      />
    </div>
  )
}

export default ResultsDisplay