import React from 'react'

const SearchBar = ({ placeholder, updateQueryParams, q }) => {
  const onChange = (e) => {
    const value = e.currentTarget.value;
    updateQueryParams({q: value});
  }

  return(
    <form className='search-bar'>
      <div className='label'>
        Search
      </div>
      <div className="input">
        <div className='wrapper'>
          <i className="material-icons">search</i>
          <input
            className='search-input'
            placeholder={placeholder}
            onChange={onChange}
            value={q||''}
          />
        </div>
      </div>
    </form>
  )
}

export default SearchBar;