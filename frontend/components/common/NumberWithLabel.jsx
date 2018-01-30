import React, { Component } from 'react'
import CountUp, { startAnimation } from 'react-countup';
import VisibilitySensor from 'react-visibility-sensor';

export default class NumberWithLabel extends Component {
  constructor(props) {
    super(props);
    this.triggerCountup = () => this._triggerCountup()
    this.handleVisibilityChange = (e) => this._handleVisibilityChange(e)
  }

  _triggerCountup() {
    startAnimation(this.countUpNum);
  }

  _handleVisibilityChange(isVisible) {
    if (isVisible) {
      this.triggerCountup();
    }
  }

  render() {

    return (
      <VisibilitySensor onChange={this.handleVisibilityChange}>
        <div className="stat">
          <CountUp
            className="number"
            start={0}
            end={this.props.number}
            duration={2}
            ref={(el) => {this.countUpNum = el}}
          />
          <span className='text'>
            { this.props.label }
          </span>
        </div>
      </VisibilitySensor>
    );
  }

}

