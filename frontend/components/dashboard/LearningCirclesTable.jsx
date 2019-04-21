import React, { Component } from "react";
import axios from "axios";
import { DISCOURSE_API_URL } from "../../helpers/constants";
import ApiHelper from "../../helpers/ApiHelper";
import GenericTable from "./GenericTable";
import moment from "moment";


export default class LearningCirclesTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      learningCircles: []
    };
    this.populateResources = () => this._populateResources();
  }

  componentDidMount() {
    this.populateResources();
  }

  _populateResources() {
    const api = new ApiHelper('learningCircles');
    const userEmail = this.props.userEmail || null;

    const onSuccess = (data) => {
      this.setState({ learningCircles: data.items })
    }

    api.fetchResource({ callback: onSuccess, params: { limit: 10, user: true, scope: this.props.scope } })
  }

  render() {
    console.log(this.state)

    return (
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <td>Course</td>
              <td>Venue</td>
              <td>Signups</td>
              <td>Start date</td>
              <td>Actions</td>
            </tr>
          </thead>
          <tbody>
            {
              this.state.learningCircles.map(lc => {
                const startDate = moment(lc.start_date).format('MMM D, YYYY')
                const classes = lc.draft ? 'bg-secondary' : '';

                return(
                  <tr key={lc.id} className={`${classes}`}>
                    <td><a href={"/"}>{`${lc.draft ? "[DRAFT] " : ""}${lc.course.title}`}</a></td>
                    <td>{lc.venue}</td>
                    <td>{"0"}</td>
                    <td>{startDate}</td>
                    <td><a href={lc.url} className="p2pu-btn btn-small dark">edit</a></td>
                  </tr>
                )
              })
            }
          </tbody>
        </table>
      </div>
    );
  }
}
