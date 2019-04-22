import React, { Component } from "react";
import axios from "axios";
import { DISCOURSE_API_URL } from "../../helpers/constants";
import ApiHelper from "../../helpers/ApiHelper";
import GenericTable from "./GenericTable";
import moment from "moment";


export default class UpcomingMeetings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      meetings: [],
      errors: []
    };
    this.populateResources = () => this._populateResources();
  }

  componentDidMount() {
    this.populateResources();
  }

  _populateResources() {
    const api = new ApiHelper('landingPage');

    const onSuccess = (data) => {
      if (data.status && data.status === "error") {
        return this.setState({ errors: data.errors })
      }

      this.setState({ meetings: data.items })
    }

    api.fetchResource({ callback: onSuccess, params: { scope: this.props.scope } })
  }

  generateFormattedMeetingDate = (nextMeeting) => {
    if (moment().isSame(nextMeeting, 'day')) {
      return 'Today'
    } else if (moment().add(1, 'day').isSame(nextMeeting, 'day')) {
      return 'Tomorrow'
    } else {
      return nextMeeting.format('dddd, MMM Do')
    }
  }

  render() {
    if (this.state.meetings.length === 0) {
      return(
        <div className="py-2">
          <div>{this.state.errors}</div>
        </div>
      )
    };

    return (
      <div className="">
        {
          this.state.meetings.map(meeting => {
            const nextMeeting = moment(`${meeting.next_meeting_date} ${meeting.meeting_time}`);
            const formattedMeetingDate = this.generateFormattedMeetingDate(nextMeeting);
            const formattedStartTime = nextMeeting.format('h:mma');
            const formattedCity = meeting.city.replace(/United States of America/, 'USA');
            const imgSrc = meeting.image_url ? meeting.image_url : '/static/images/learning-circle-default.jpg';

            return(
              <div className="meeting-card py-3 row" key={meeting.course.id}>
                <div className="col-sm-12 col-md-2">
                  <img className="img-thumbnail" src={imgSrc} />
                </div>

                <div className="content col-sm-12 col-md-10">
                  <div className="d-flex">

                    <div className="minicaps text-xs d-flex align-items-center mr-3">
                      <i className="material-icons pr-1">today</i>
                      <span className="bold">{`${formattedMeetingDate} at ${formattedStartTime}`}</span>
                    </div>

                    <div className="minicaps text-xs d-flex align-items-center mr-3">
                      <i className="material-icons pr-1">location_on</i>
                      <span className="bold">{formattedCity}</span>
                    </div>

                    <a href={meeting.course.link}>
                      <div className="minicaps text-xs d-flex align-items-center mr-3">
                        <i className="material-icons pr-1">launch</i>
                        <span className="bold">Course thread</span>
                      </div>
                    </a>

                  </div>

                  <div className="info">
                    <p className='meeting-info my-1'>
                      <span className="bold">{meeting.facilitator}</span> is facilitating a learning circle on <span className="bold">{meeting.course.title}</span> at { meeting.venue }
                    </p>
                  </div>

                </div>
              </div>
            )
          })
        }
      </div>
    );
  }
}
