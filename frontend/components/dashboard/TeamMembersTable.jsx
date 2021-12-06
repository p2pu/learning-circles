import React, { Component, useRef, useEffect } from "react";
import ApiHelper from "../../helpers/ApiHelper";
import axios from "axios"

const PAGE_LIMIT = 5;

// TODO - click on remove, pop up modal for confirmation, on confirmation, POST delete and reload API results?


const ConfirmMemberRemoval = props => {
  const {member, onDeletionAffirmed, onDeletionCancelled} = props;

  const alert = useRef(null);
  useEffect(() => {
    let offset = alert.current.getBoundingClientRect().y;
    window.scrollBy(0, offset - 160);
  }, []);

  return (
    <div className="alert alert-danger" ref={alert}>
      <form onSubmit={e => {e.preventDefault(); onDeletionAffirmed(member.id)}}>
        <p>Are you sure you want to delete <strong>{ member.facilitator.first_name } &lt;{ member.facilitator.email }&gt;</strong> ?</p>
        <button className="p2pu-btn btn btn-sm orange" type="submit">Delete</button>
        <button 
          className="p2pu-btn btn btn-sm gray" 
          onClick={e => { e.preventDefault(); onDeletionCancelled()} }
        >Cancel</button>
      </form>
    </div>
  )
}

export default class TeamMembersTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      teamMembers: [],
      limit: PAGE_LIMIT,
      count: 0,
      memberToDelete: null,
      deleteConfirmation: [null, null],
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = (params={}) => {
    const api = new ApiHelper('teamMembers');

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

  handleDeleteMember = memberId => {
    const url = `${this.props.deleteTeamMembershipApiUrl}${memberId}/` 
    axios({
      url,
      method: 'DELETE',
    }).then(res => {
      console.log(res)
      if (res.status === 204) {
        this.setState({
          memberToDelete: null,
          deleteConfirmation: ['success', 'Member was deleted.'],
        });
        const params = { limit: PAGE_LIMIT, offset: this.state.offset };
        this.populateResources(params)
      } else {
        this.setState({
          memberToDelete: null,
          deleteConfirmation: ['warning', 'Could not delete team member.'],
        });
      }
    }).catch(err => {
      console.log(err);
      this.setState({
        memberToDelete: null,
        deleteConfirmation: ['warning', 'Could not delete team member.'],
      });
    })
  }

  handleRemoveClick = member => {
    this.setState({memberToDelete: member, deleteConfirmation: [null, null]});
  }

  render() {
    const totalPages = Math.ceil(this.state.count / PAGE_LIMIT);
    const currentPage = Math.ceil((this.state.offset + this.state.teamMembers.length) / PAGE_LIMIT);

    if (this.state.teamMembers.length === 0) {
      return(
        <div className="py-2">
          <div>You don't have any team members.</div>
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
        { this.state.memberToDelete &&
          <ConfirmMemberRemoval
            member={this.state.memberToDelete}
            onDeletionAffirmed={this.handleDeleteMember}
            onDeletionCancelled={() => {this.setState({memberToDelete: null}); }}
          />
        }
        <div className="table-responsive d-none d-md-block">
          <table className="table">
            <thead>
              <tr>
                <td>Name</td>
                <td>Email</td>
                <td>Role</td>
                <td>Joined P2PU</td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {
                this.state.teamMembers.map(m => {
                  const facilitator = m.facilitator
                  return(
                    <tr key={ m.id }>
                      <td>{`${facilitator.first_name} ${facilitator.last_name}`}</td>
                      <td>{ facilitator.email }</td>
                      <td>{ m.role }</td>
                      <td>{ facilitator.email_confirmed_at }</td>
                      <td>
                        <button 
                          className="p2pu-btn btn btn-sm secondary orange"
                          onClick={() => this.handleRemoveClick(m)}
                        >remove</button>
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
                      <div></div>
                    </div>

                    <div className="flex-grow px-2">
                      <div className="">{`${facilitator.first_name} ${facilitator.last_name}`}</div>
                      <div className="">{ facilitator.email }</div>
                      <div className="">{ m.role }</div>
                      <div className="">{ m.created_at }</div>
                      <div>
                        <button 
                          className="p2pu-btn btn btn-sm secondary orange"
                          onClick={() => this.handleRemoveClick(m)}
                        >remove</button>
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
