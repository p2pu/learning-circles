import React from 'react'
import SearchBar from './SearchBar'
import FiltersSection from './FiltersSection'

const SearchAndFilter = (props) => {
  const noResults = props.searchResults.length === 0;

  return(
    <div className='search-container'>
      { noResults && <div className='overlay'></div> }
      <SearchBar
        placeholder={props.placeholder}
        updateQueryParams={props.updateQueryParams}
      />
      <FiltersSection
        filterCollection={props.filterCollection}
        updateQueryParams={props.updateQueryParams}
        searchSubject={props.searchSubject}
        {...props}
      />
    </div>
  )
}

export default SearchAndFilter;