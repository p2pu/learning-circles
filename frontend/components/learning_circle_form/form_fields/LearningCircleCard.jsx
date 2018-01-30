import React, { Component } from 'react'
import ReactDOM from 'react-dom'

const LearningCircleCard = (props) => {

  const goToUrl = () => {
    window.location.href = props.url;
  }

  return (
    <div className="result-item grid-item col-md-4 col-sm-12 col-xs-12">
      <div className="card" onClick={ goToUrl }>
        <div className='card-title'>
          <h4 className="title">{ props.name }</h4>
        </div>

        <div className="image-container hidden-on-mobile">
          <div className="image">
            {
              props.image &&
              <img src={ props.image } alt={ props.name } />
            }
          </div>
        </div>

        <div className='card-body'>
          <p className="schedule">
            <i className="material-icons">schedule</i>
            { props.schedule }
          </p>
          <p className="duration">
            <i className="material-icons">today</i>
            { props.duration }
          </p>
          <p className="city-country">
            <i className="material-icons">place</i>
            { props.city }
          </p>
          <p className="facilitator">
            <i className="material-icons">face</i>
            Facilitated by { props.facilitator }
          </p>
          <p className="location">
            <i className="material-icons">store</i>
            Meeting at { props.location }
          </p>
          <div className='actions'>
            <div className="primary-cta">
              <a href={ props.url } className=''>
                <button className="btn p2pu-btn transparent">Sign up</button>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LearningCircleCard
