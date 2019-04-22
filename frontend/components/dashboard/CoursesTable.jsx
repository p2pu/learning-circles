import React, { Component } from "react";
import axios from "axios";
import { DISCOURSE_API_URL } from "../../helpers/constants";
import ApiHelper from "../../helpers/ApiHelper";
import GenericTable from "./GenericTable";
import moment from "moment";


export default class CoursesTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      courses: []
    };
    this.populateResources = () => this._populateResources();
  }

  componentDidMount() {
    this.populateResources();
  }

  _populateResources() {
    const api = new ApiHelper('courses');

    const onSuccess = (data) => {
      this.setState({ courses: data.items })
    }

    api.fetchResource({ callback: onSuccess, params: { limit: 10, user: true, include_unlisted: true } })
  }

  render() {
    if (this.state.courses.length === 0) {
      return(
        <div className="py-2">
          <div>You haven't added any courses.</div>
          <a href={"/en/course/create"} className="p2pu-btn dark btn-small ml-0">Add a course</a>
        </div>
      )
    };
    return (
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <td>Title</td>
              <td>Provider</td>
              <td>Date Added</td>
              <td>Actions</td>
            </tr>
          </thead>
          <tbody>
            {
              this.state.courses.map(course => {
                const date = moment(course.created_at).format('MMM D, YYYY')
                const classes = course.unlisted ? 'bg-secondary' : '';

                return(
                  <tr key={course.id} className={`${classes}`}>
                    <td><a href={course.course_page_url}>{`${course.unlisted ? "[UNLISTED] " : ""}${course.title}`}</a></td>
                    <td>{course.provider}</td>
                    <td>{date}</td>
                    <td><a href={course.course_edit_url} className="p2pu-btn btn-small dark">edit</a></td>
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
