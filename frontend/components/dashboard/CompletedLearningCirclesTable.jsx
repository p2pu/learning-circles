import React, { Component } from "react";
import ApiHelper from "../../helpers/ApiHelper";
import moment from "moment";

const PAGE_LIMIT = 5;

export default class LearningCirclesTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      learningCircles: [],
      limit: PAGE_LIMIT,
      count: 0
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('learningCircles');

    const onSuccess = (data) => {
      this.setState({ learningCircles: data.items, count: data.count, offset: data.offset, limit: data.limit })
    }

    const defaultParams = { limit: this.state.limit, offset: this.state.offset, user: this.props.user, team_id: this.props.teamId, scope: "completed" }

    api.fetchResource({ callback: onSuccess, params: { ...defaultParams, ...params } })
  }

  nextPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset + this.state.learningCircles.length };
    this.populateResources(params)
  }

  prevPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset - PAGE_LIMIT };
    this.populateResources(params)
  }

  render() {
    const totalPages = Math.ceil(this.state.count / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.learningCircles.length) / PAGE_LIMIT);

    if (this.state.learningCircles.length === 0) {
      return(
        <div className="py-2">
          <div>No completed learning circles.</div>
        </div>
      )
    };

    return (
      <div className="learning-circles-table">
        <div className="table-responsive d-none d-md-block">
          <table className="table">
            <thead>
              <tr>
                <td>Learning circle</td>
                <td>Venue</td>
                { this.props.teamId && <td>Facilitator</td>}
                <td>Signups</td>
                <td>Last meeting</td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {
                this.state.learningCircles.map(lc => {
                  const date = lc.last_meeting_date ? moment(lc.last_meeting_date).format('MMM D, YYYY') : "n/a";
                  const classes = lc.draft ? 'bg-cream-dark' : '';

                  return(
                    <tr key={ lc.id } className={`${classes}`}>
                      <td>{`${lc.draft ? "[DRAFT] " : ""}${lc.name}`}</td>
                      <td>{ lc.venue }</td>
                      { this.props.teamId && <td>{ lc.facilitator }</td>}
                      <td>{ (lc.is_facilitator || this.props.teamId)?lc.signup_count:'N/A' }</td>
                      <td>{ date }</td>
                      <td>
                        { (lc.is_facilitator || this.props.userIsOrganizer) && <a href={ lc.studygroup_path } className="p2pu-btn btn btn-sm dark">manage</a>}
                        { lc.is_learner && <a href={`/studygroup/${lc.id}/learn/`} className="p2pu-btn btn btn-sm blue">Learner dash</a> }
                      </td>
                    </tr>
                  )
                })
              }
            </tbody>
          </table>
        </div>

        <div className="d-md-none">
          {
            this.state.learningCircles.map(lc => {
              const date = lc.last_meeting_date ? moment(lc.last_meeting_date).format('MMM D, YYYY') : "n/a";
              const classes = lc.draft ? 'bg-cream-dark' : '';

              return(
                <div className={`meeting-card p-2 ${classes}`} key={lc.id}>
                  <strong className="bold">{`${lc.draft ? "[DRAFT] " : ""}${lc.name}`}</strong>

                  <div className="d-flex">
                    <div className="pr-2">
                      <div className="bold">Venue</div>
                      { (lc.is_facilitator || this.props.teamId ) && <div className="bold">Signups</div> }
                      <div className="bold">Last Meeting</div>
                    </div>

                    <div className="flex-grow px-2">
                      <div className="">{ lc.venue }</div>
                      { ( lc.is_facilitator || this.props.teamId ) && <div className="">{ lc.signup_count }</div> }
                      <div className="">{ date }</div>
                    </div>
                  </div>

                  { (lc.is_facilitator || this.props.userIsOrganizer) && <a href={ lc.studygroup_path } className="p2pu-btn btn btn-sm dark m-0 my-2">manage</a> }
                  { lc.is_learner && <a href={`/studygroup/${lc.id}/learn/`} className="p2pu-btn btn btn-sm blue">Learner dash</a> }
                </div>
              )
            })
          }
        </div>
        {
          totalPages > 1 &&
          <nav aria-label="Page navigation">
            <ul className="pagination">
              <li className={`page-item ${currentPage <= 1 ? 'disabled' : ''}`}>
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
