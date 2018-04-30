import React from 'react'
import { take } from 'lodash'

import { Card, CardTitle, CardBody, UsageBadge } from '../Card';

const CourseCard = (props) => {

  const feedbackPage = `https://etherpad.p2pu.org/p/course-feedback-${props.course.id}`;
  const availability = props.course.on_demand ? 'Course available on demand' : 'Check course availability';
  const handleFilterClick = (topic) => {
    return () => { props.updateQueryParams({ topics: [topic] }) }
  };
  const topicsList = take(props.course.topics, 5).map((topic) => {
    return <a className='tag' onClick={handleFilterClick(topic)}>{topic}</a>
  });

  return (
    <Card>
      <UsageBadge number={props.course.learning_circles} id={props.id} />
      <CardTitle>{ props.course.title }</CardTitle>
      <CardBody>
        <p className="caption">{ props.course.caption }</p>
        <div className="divider"></div>
        <p className="tags small-caps">
          <i className="material-icons">label_outline</i>
          <span className='topics-list'>
            { topicsList.map((topic, index) => {
              return <span key={index}>{!!index && ', '}{topic}</span>
            })}
          </span>
        </p>
        <p className="provider small-caps">
          <i className="material-icons">school</i>
          { `Provided by ${props.course.provider}` }
        </p>
        <p className="availability small-caps">
          <i className="material-icons">schedule</i>
          { availability }
        </p>
        <div className="divider"></div>
        <div className='actions'>
          <div className="secondary-cta">
            <a href={props.course.link} target='_blank'>
              <i className="material-icons">open_in_new</i>See the course
            </a>
            <a href={feedbackPage} target='_blank'>
              <i className="material-icons">open_in_new</i>Facilitator feedback
            </a>
          </div>
          <div className="primary-cta">
          {
            props.onSelectResult &&
            <div className="primary-cta">
              <button onClick={() => props.onSelectResult(props.course)} className="btn p2pu-btn transparent">{props.buttonText}</button>
            </div>
          }
          </div>
        </div>
      </CardBody>
    </Card>
  );
}

export default CourseCard
