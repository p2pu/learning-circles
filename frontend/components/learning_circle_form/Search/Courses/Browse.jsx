import React from 'react'
import Masonry from 'react-masonry-component'
import CourseCard from './CourseCard.jsx'

const BrowseCourses = ({ results, updateQueryParams, onSelectResult }) => {
  return (
    <Masonry className={"search-results row grid"}>
      {
        results.map((course, index) => (
          <CourseCard
            key={`course-card-${index}`}
            id={`course-card-${index}`}
            course={course}
            updateQueryParams={updateQueryParams}
            onSelectResult={onSelectResult}
            buttonText='Use this course'
          />
        ))
      }
    </Masonry>
  );
}


export default BrowseCourses
