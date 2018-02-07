import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import Masonry from 'react-masonry-component'
import CourseCard from './CourseCard.jsx'


export default class BrowseCourses extends Component {

  constructor(props) {
    super(props);
  }

  componentWillReceiveProps(newProps) {
    if (newProps != this.props) {
      console.log('masonry layout')
      this.masonry.layout();
    }
  }

  render() {
    return (
      <Masonry className={"search-results row grid"} ref={(c) => {this.masonry = this.masonry || c.masonry;}}>
        {
          this.props.courses.map((course, index) => {
            return(
              <CourseCard
                key={index}
                id={`course-card-${index}`}
                course={course}
                updateQueryParams={this.props.updateQueryParams}
                updateFormData={this.props.updateFormData}
              />
            )
          })
        }
      </Masonry>
    );
  }
}

