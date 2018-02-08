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
      this.masonry.layout();
    }
  }

  render() {
    return (
      <Masonry className={"search-results row grid"} ref={(c) => {this.masonry = this.masonry || c.masonry;}}>
        {
          this.props.courses.map((course, index) => {
            const handleSelect = () => {
              this.props.updateFormData({ course });
              this.props.scrollToTop;
            };

            return(
              <CourseCard
                key={index}
                id={`course-card-${index}`}
                course={course}
                handleSelect={handleSelect}
                buttonText='Use this course'
              />
            )
          })
        }
      </Masonry>
    );
  }
}

