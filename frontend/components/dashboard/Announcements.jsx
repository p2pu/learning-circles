import React, { Component } from "react";
import moment from "moment";
import AOS from 'aos';

import ApiHelper from "../../helpers/ApiHelper";
import { DEFAULT_LC_IMAGE } from "../../helpers/constants"
import Card from './Card';

export default class Announcements extends Component {
  constructor(props) {
    super(props);
    this.state = {
      announcements: [],
      errors: [],
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
    const api = new ApiHelper('announcements');

    const onSuccess = (data) => {
      if (data.status && data.status === "error") {
        return this.setState({ errors: data.errors })
      }

      this.setState({ announcements: data.items })
    }

    api.fetchResource({ callback: onSuccess })
  }

  render() {
    if (this.state.errors.length > 0 || this.state.announcements.length === 0) {
      return null
    };

    return (
      <div className="">
        {
          this.state.announcements.map((announcement, index) => {
            return(
              <Card className={`bg-${announcement.color} feedback-survey d-block w-100`} key={`announcement-${index}`}>
                <div className="bold text-center text-white">{announcement.text}</div>
                <div className="text-center mt-3">
                  <a href={announcement.link} className="p2pu-btn light btn-sm" target="_blank">{announcement.link_text}</a>
                </div>
              </Card>
            )
          })
        }
      </div>
    );
  }
}
