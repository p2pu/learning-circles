import React from 'react'
import SearchBar from './SearchBar'
import FiltersSection from './Filters/FiltersSection'

const SearchAndFilter = (props) => {
  const noResults = props.searchResults.length === 0;

  return(
    <div className='search-container'>
      { noResults && <div className='overlay'></div> }
      <SearchBar
        placeholder={props.placeholder}
        updateQueryParams={props.updateQueryParams}
        q={props.q}
      />
      <FiltersSection
        {...props}
      />
    </div>
  )
}

export default SearchAndFilter;