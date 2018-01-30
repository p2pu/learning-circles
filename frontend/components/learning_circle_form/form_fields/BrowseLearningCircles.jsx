import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import Masonry from 'react-masonry-component'
import LearningCircleCard from './LearningCircleCard.jsx'
import moment from 'moment'

const BrowseLearningCircles = (props) => {

  return (
    <Masonry className={"search-results row grid"}>
      {
        props.learningCircles.map((circle, index) => {
          const startDate = moment(`${circle.start_date} ${circle.meeting_time}`);
          const endDate = moment(`${circle.start_date} ${circle.end_time}`);
          const formattedDate = startDate.format('MMMM Do, YYYY');
          const formattedStartTime = startDate.format('h:mma');
          const formattedEndTime = endDate.format('h:mma');
          const schedule = `${circle.day} from ${formattedStartTime} to ${formattedEndTime} (${circle.time_zone})`;
          const duration = `${circle.weeks} weeks starting ${formattedDate}`;

          return(
            <LearningCircleCard
              key={index}
              name={ circle.course.title }
              url={ circle.url }
              schedule={ schedule }
              facilitator={ circle.facilitator }
              location={ circle.venue }
              duration={ duration }
              image={ circle.image_url }
              city={ circle.city }
            />
          )
        })
      }
      <div className="result-item grid-item col-md-4 col-sm-12 col-xs-12 start-learning-circle">
        <div className="circle">
          <p>Start a learning circle in your neighborhood</p>
          <a href="/en/facilitate" className="btn p2pu-btn dark arrow"><i className="fa fa-arrow-right" aria-hidden="true"></i></a>
        </div>
      </div>
    </Masonry>
  );
}

export default BrowseLearningCircles
