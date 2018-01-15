import React from 'react'

const SearchBar = ({ placeholder, updateQueryParams }) => {
  const onSubmit = (e) => {
    e.preventDefault();
    const query = document.querySelector('.search-input').value

    updateQueryParams({q: query});
    e.currentTarget.reset();
  }

  return(
    <form className='search-bar' onSubmit={onSubmit}>
      <div className='label'>
        Search
      </div>
      <div className="input">
        <div className='wrapper'>
          <i className="material-icons">search</i>
          <input className='search-input' placeholder={placeholder} />
        </div>
        <button className='p2pu-btn blue' type='submit'>Search</button>
      </div>
    </form>
  )
}

export default SearchBar;