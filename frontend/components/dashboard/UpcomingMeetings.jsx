import React, { Component } from "react";
import moment from "moment";
import AOS from 'aos';

import ApiHelper from "../../helpers/ApiHelper";
import { DEFAULT_LC_IMAGE } from "../../helpers/constants"


export default class UpcomingMeetings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      meetings: [],
      errors: []
    };
  }

  componentDidMount() {
    this.populateResources();
    AOS.init();
  }

  componentDidUpdate() {
    AOS.refresh();
  }

  populateResources = () => {
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
    if (this.state.errors.length > 0) {
      return(
        <div className="py-2">
          <div>
            <a href="https://www.p2pu.org/en/organize/">Check out our organizer materials</a> if you’re interested in starting a team.
          </div>
        </div>
      )
    };

    if (this.state.meetings.length === 0) {
      return(
        <div className="py-2">
          <div>No upcoming meetings.</div>
        </div>
      )
    }

    return (
      <div className="">
        {
          this.state.meetings.map((meeting, index) => {
            const nextMeeting = moment(`${meeting.next_meeting_date} ${meeting.meeting_time}`);
            const formattedMeetingDate = this.generateFormattedMeetingDate(nextMeeting);
            const formattedStartTime = nextMeeting.format('h:mma');
            const formattedCity = meeting.city.replace(/United States of America/, 'USA');
            const delay = index * 100;
            const imageSrc = meeting.image_url || DEFAULT_LC_IMAGE;

            return(
              <div className="meeting-card py-3 row" key={`meeting-${meeting.course.id}-${index}`} data-aos='fade-up' data-aos-delay={delay}>
                <div className="d-none d-sm-block col-sm-4 col-md-2 image-thumbnail">
                   <a href={meeting.url}>
                    <img className="img-thumbnail" src={imageSrc} />
                  </a>
                </div>

                <div className="content col-12 col-sm-8 col-md-10">
                  <div className="d-sm-block d-lg-flex mb-2">

                    <div className="minicaps text-xs d-flex align-items-center mr-3">
                      <i className="material-icons pr-1">today</i>
                      <span className="bold">{`${formattedMeetingDate} at ${formattedStartTime}`}</span>
                    </div>

                    <div className="minicaps text-xs d-flex align-items-center mr-3">
                      <i className="material-icons pr-1">location_on</i>
                      <span className="bold">{formattedCity}</span>
                    </div>
                  </div>

                  <div className="info">
                    <p className='meeting-info mb-0'>
                      <span className="">{meeting.facilitator}</span> is facilitating <a href={meeting.url}>{meeting.name}</a> at { meeting.venue }
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
