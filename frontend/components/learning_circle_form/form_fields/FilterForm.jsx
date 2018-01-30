import React, { Component } from 'react'
import LocationFilterForm from './LocationFilterForm'
import TopicsFilterForm from './TopicsFilterForm'
import MeetingDaysFilterForm from './MeetingDaysFilterForm'
import OrderCoursesForm from './OrderCoursesForm'

const FilterForm = (props) => {
  const closeFilter = () => { props.updateActiveFilter(null) };
  const openClass = props.activeFilter ? 'open' : '';

  const internalForm = () => {
    switch (props.activeFilter) {
      case 'location':
      return <LocationFilterForm {...props} closeFilter={closeFilter} />;
      case 'topics':
      return <TopicsFilterForm {...props} />;
      case 'meetingDays':
      return <MeetingDaysFilterForm { ...props} />;
      case 'orderCourses':
      return <OrderCoursesForm { ...props} />;
    }
  }

  return(
    <div className={`filter-form-dropdown ${openClass}`}>
      <div className='close' style={{ textAlign: 'right', float: 'none' }}>
        <i className="material-icons" onClick={closeFilter}>close</i>
      </div>
      {internalForm()}
    </div>
  )
}

export default FilterForm;
