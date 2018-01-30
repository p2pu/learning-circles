import React from 'react'

const Filter = ({filter, active, updateActiveFilter}) => {
  const filterNames = {
    'location': 'Location',
    'topics': 'Topics',
    'meetingDays': 'Meeting Day(s)',
    'orderCourses': 'Order by'
  }

  const iconName = active ? 'remove' : 'add'

  const activeClass = active ? 'active' : ''

  const handleClick = () => {
    const newValue = active ? '' : filter
    updateActiveFilter(newValue)
  }

  return(
    <div className={`filter ${activeClass}`} >
      <button className='p2pu-btn light with-outline' onClick={handleClick}>
        <span style={{ display: 'flex',flexWrap: 'nowrap' }}>
          {filterNames[filter]}
        </span>
      </button>
    </div>
  )
}

export default Filter;