import React, { Component } from "react";
import ApiHelper from "../../helpers/ApiHelper";
import axios from "axios"

const PAGE_LIMIT = 5;

export default class TeamMembersTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      teamMembers: [],
      limit: PAGE_LIMIT,
      count: 0,
      deleteConfirmation: [null, null],
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('teamInvitations');

    const onSuccess = (data) => {
      this.setState({ teamMembers: data.items, count: data.count, offset: data.offset, limit: data.limit })
    }

    const defaultParams = { limit: this.state.limit, offset: this.state.offset, team_id: this.props.teamId }

    api.fetchResource({ callback: onSuccess, params: { ...defaultParams, ...params } })
  }

  nextPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset + this.state.teamMembers.length };
    this.populateResources(params)
  }

  prevPage = (e) => {
    e.preventDefault();
    const params = { limit: PAGE_LIMIT, offset: this.state.offset - PAGE_LIMIT };
    this.populateResources(params)
  }

  handleDeleteInvitation = invitationId => {
    const url = `${this.props.deleteTeamInvitationApiUrl}${invitationId}/`
    axios({
      url,
      method: 'DELETE',
    }).then(res => {
      console.log(res)
      if (res.status === 204) {
        this.setState({
          deleteConfirmation: ['success', 'Invitation was cancelled.'],
        });
        const params = { limit: PAGE_LIMIT, offset: this.state.offset };
        this.populateResources(params)
      } else {
        this.setState({
          deleteConfirmation: ['warning', 'Could not cancel invitation.'],
        });
      }
    }).catch(err => {
      console.log(err);
      this.setState({
        deleteConfirmation: ['warning', 'Could not cancel invitation.'],
      });
    })
  }


  render() {
    const totalPages = Math.ceil(this.state.count / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.teamMembers.length) / PAGE_LIMIT);

    if (this.state.teamMembers.length === 0) {
      return(
        <div className="py-2">
          <div>You don't have any pending invitations.</div>
        </div>
      )
    }

    return (
      <div className="learning-circles-table">
        { this.state.deleteConfirmation[0] && 
          <div className={`alert alert-${this.state.deleteConfirmation[0]}`}>
            {this.state.deleteConfirmation[1]}
          </div>
        }
        <div className="table-responsive d-none d-md-block">
          <table className="table">
            <thead>
              <tr>
                <td>Email</td>
                <td>Role</td>
                <td>Invitation sent</td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {
                this.state.teamMembers.map(m => {
                  const facilitator = m.facilitator
                  return(
                    <tr key={ m.id }>
                      <td>{ facilitator.email }</td>
                      <td>{ m.role }</td>
                      <td>{ m.created_at }</td>
                      <td>
                        <button onClick={e => {this.handleDeleteInvitation(m.id)}} className="p2pu-btn btn btn-sm orange">cancel</button>
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
            this.state.teamMembers.map(m => {
              const facilitator = m.facilitator
              return(
                <div className={`meeting-card p-2`} key={m.id}>
                  <div className="d-flex">
                    <div className="pr-2">
                      <div className="bold">Name</div>
                      <div className="bold">Email</div>
                      <div className="bold">Role</div>
                      <div className="bold">Joined</div>
                    </div>

                    <div className="flex-grow px-2">
                      <div className="">{`${facilitator.first_name} ${facilitator.last_name}`}</div>
                      <div className="">{ facilitator.email }</div>
                      <div className="">{ m.role }</div>
                      <div className="">{ m.created_at }</div>
                      <div>
                        <button onClick={e => {this.handleDeleteInvitation(m.id)}} className="p2pu-btn btn btn-sm orange">cancel</button>
                      </div>
                    </div>
                  </div>
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
