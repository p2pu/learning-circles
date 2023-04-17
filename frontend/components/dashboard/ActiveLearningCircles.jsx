import React, {useEffect, useState} from 'react';

import ApiHelper from "../../helpers/ApiHelper";

const imgStyle = {
  width: "auto",
  display: "inline-block",
  height: "150px",
  border: "5px solid #05c6b4",
  'border-radius': "100%",
  'z-index': "9",
}

const cardStyle = {
  margin: 0,
  'margin-left': "-75px",
  'padding-left': "calc(75px + 1rem)",
  'z-index': "8",
}

const ActiveLearningCircle = ({image, name, venue, ...props}) => (
  <div className="d-flex pb-4">
    <img style={imgStyle} src={image || "/static/images/learning-circle-default.jpg"} />
    <div className="card" style={cardStyle} >
      <h5 className="card-title">{name}</h5>
      <div className="row">
      <div className="col-9">
        <p>Venue: {venue}</p>
        <p>Next meeting: {props.next_meeting_date}</p>
      </div>
      <div className="col-3">
        <a className="btn p2pu-btn blue" href={`/studygroup/${props.id}/learn/`}>Learner dash</a> 
      </div>
      </div>
    </div>
  </div>
);

const ActiveLearningCircles = props => {
  
  const [learningCircles, setLearningCircles] = useState([]);

  useEffect( () => {
    const api = new ApiHelper('learningCircles');
    const onSuccess = (data) => {
      setLearningCircles(data.items);
      //TODO, count: data.count, offset: data.offset, limit: data.limit })
    }
    const defaultParams = { user: true, draft: false, scope: "active" }
    api.fetchResource({ callback: onSuccess, params: defaultParams });
  }, []);

  return (
    <div>
      <h4>Active learning circles</h4>
      { learningCircles.map( (lc, i) => <ActiveLearningCircle key={i} {...lc} />) }
    </div>
  );
}

export default ActiveLearningCircles;
