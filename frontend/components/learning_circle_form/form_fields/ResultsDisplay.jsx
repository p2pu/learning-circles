import React from 'react'
import BrowseLearningCircles from './BrowseLearningCircles'
import SearchTags from './SearchTags'

const ResultsDisplay = (props) => {
  const resetSearch = () => { window.location.reload() };

  return(
    <div className="search-results col-sm-12">
      <SearchTags {...props} />
      <BrowseLearningCircles learningCircles={props.searchResults} />
    </div>
  )
}

export default ResultsDisplay