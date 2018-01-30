import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import Masonry from 'react-masonry-component'
import CourseCard from './CourseCard.jsx'

const BrowseCourses = (props) => {
  return (
    <Masonry className={"search-results row grid"}>
      {
        props.courses.map((course, index) => {
          return(
            <CourseCard
              key={index}
              id={`course-card-${index}`}
              course={course}
              updateQueryParams={props.updateQueryParams}
              updateFormData={props.updateFormData}
            />
          )
        })
      }
    </Masonry>
  );
}


export default BrowseCourses
