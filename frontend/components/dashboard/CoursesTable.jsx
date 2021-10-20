import React, { Component } from "react";
import ApiHelper from "../../helpers/ApiHelper";
import moment from "moment";
import AOS from 'aos';

const PAGE_LIMIT = 5;


export default class CoursesTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      courses: [],
      limit: PAGE_LIMIT,
      count: 0,
      offset: 0,
    };
  }

  componentDidMount() {
    this.populateResources();
    AOS.init();
  }

  componentDidUpdate() {
    AOS.refresh();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('courses');

    const onSuccess = (data) => {
      this.setState({ courses: data.items, count: data.count, offset: data.offset, limit: data.limit })
    }

    const defaultParams = { limit: this.state.limit, offset: this.state.offset, user: true, include_unlisted: true }

    api.fetchResource({ callback: onSuccess, params: { ...defaultParams, ...params } })
  }

  nextPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset + this.state.courses.length };
    this.populateResources(params)
  }

  prevPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset - PAGE_LIMIT };
    this.populateResources(params)
  }

  render() {
    const totalPages = Math.ceil(this.state.count / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.courses.length) / PAGE_LIMIT);

    if (this.state.courses.length === 0) {
      return(
        <div className="py-2">
          <div>You haven't added any courses.</div>
          <a href={"/en/course/create"} className="p2pu-btn dark btn btn-sm ml-0">Add a course</a>
        </div>
      )
    };

    return (
      <div className="learning-circles-table">
        <div className="table-responsive d-none d-md-block" data-aos='fade'>
          <table className="table">
            <thead>
              <tr>
                <td>Title</td>
                <td>Provider</td>
                <td>Date Added</td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {
                this.state.courses.map(course => {
                  const date = moment(course.created_at).format('MMM D, YYYY')
                  const classes = course.unlisted ? 'bg-cream-dark' : '';

                  return(
                    <tr key={course.id} className={`${classes}`}>
                      <td><a href={course.course_page_path}>{`${course.unlisted ? "[UNLISTED] " : ""}${course.title}`}</a></td>
                      <td>{course.provider}</td>
                      <td>{date}</td>
                      <td><a href={course.course_edit_path} className="p2pu-btn btn btn-sm dark">edit</a></td>
                    </tr>
                  )
                })
              }
            </tbody>
          </table>
        </div>

        <div className="d-md-none">
          {
            this.state.courses.map((course, index) => {
              const date = moment(course.created_at).format('MMM D, YYYY')
              const classes = course.unlisted ? 'bg-cream-dark' : '';
              const delay = index * 100;

              return(
                <div className={`meeting-card p-2 ${classes}`} key={course.id} data-aos='fade-up' data-aos-delay={delay}>
                  <a className="bold" href={course.course_page_path}>{`${course.unlisted ? "[UNLISTED] " : ""}${course.title}`}</a>

                  <div className="d-flex">
                    <div className="pr-2">
                      <div className="bold">Provider</div>
                      <div className="bold">Date Added</div>
                    </div>

                    <div className="flex-grow px-2">
                      <div className="">{ course.provider }</div>
                      <div className="">{ date }</div>
                    </div>
                  </div>

                  <a href={ course.course_edit_path } className="p2pu-btn btn btn-sm dark m-0 my-2">edit</a>
                </div>
              )
            })
          }
        </div>

        {
          totalPages > 1 &&
          <nav aria-label="Page navigation">
            <ul className="pagination">
              <li className={`page-item ${currentPage == 1 ? 'disabled' : ''}`}>
                <a className="page-link" href="" aria-label="Previous" onClick={this.prevPage}>
                  <span aria-hidden="true">&laquo;</span>
                  <span className="sr-only">Previous</span>
                </a>
              </li>
              <li className="page-item">
                <span className="page-link disabled">{`Page ${currentPage} of ${totalPages}`}</span>
              </li>
              <li className={`page-item ${currentPage == totalPages ? 'disabled' : ''}`}>
                <a className="page-link" href="" aria-label="Next" onClick={this.nextPage}>
                  <span aria-hidden="true">&raquo;</span>
                  <span className="sr-only">Next</span>
                </a>
              </li>
            </ul>
          </nav>
        }
      </div>
    );
  }
}
