import React from 'react'
import PropTypes from 'prop-types';
import { CourseCard } from 'p2pu-search-cards'

import 'p2pu-search-cards/dist/build.css';


const SimilarCoursesPreview = ({ courses }) => {
  const course_arr = JSON.parse(courses);
  console.log(course_arr)

  return(
    <div className="search-results row">
    {
      course_arr.map(course => <CourseCard key={course.id} course={course} classes="col-lg-4" />)
    }
    </div>
  )
}


SimilarCoursesPreview.propTypes = {
    courses: PropTypes.string,
}

export default SimilarCoursesPreview
