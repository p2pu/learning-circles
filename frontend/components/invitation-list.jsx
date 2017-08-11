import React from 'react'
import PagedTable from './paged-table'
import moment from 'moment'
import Promise from 'promise-polyfill'
import 'whatwg-fetch'

export default class InvitationList extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            emailInput: '',
            inviteError: null,
            invitationsDelta: []
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleInviteClick = this.handleInviteClick.bind(this);
    }

    handleChange(e){
        this.setState({emailInput: e.target.value});
    }

    handleInviteClick(e){
        e.preventDefault();
        this.setState({inviteError: null});
        fetch(this.props.teamInviteUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // or 'same-origin'
            body: JSON.stringify({
                email: this.state.emailInput,
            })
        }).then(response => {
            return response.json();
        }).then(jsonBody => {
            if (jsonBody.status === 'CREATED'){
                let invitationsDelta = [
                    {email: this.state.emailInput, created_at: moment()},
                ];
                this.setState({
                    invitationsDelta: invitationsDelta.concat(this.state.invitationsDelta),
                    emailInput: ''
                });
            } else if (jsonBody.status === 'ERROR'){
                this.setState({inviteError: jsonBody.errors});
            }
        }).catch(ex => {
            this.setState({inviteError: gettext('Unknown error occured. Please try again later or contact support')});
        });
    }

    render(){
        let invitations = this.props.invitations.concat(this.state.invitationsDelta);
        let heading = <tr><th>{gettext("Name")}</th><th>{gettext("Date invited")}</th></tr>;
        let invitationsRows = invitations.map(invite =>
            (<tr key={invite.email}>
                <td>{invite.email}</td>
                <td>{moment(invite.created_at).format('MMMM D, Y h:m a')}</td>
            </tr>)
        );
        if (invitationsRows.length == 0){
            invitationsRows = [(<tr key="0"><td>{gettext("No pending invitations")}</td><td></td></tr>)];
        }
        let errorMsg = null;
        if (this.state.inviteError) {
            errorMsg = ( <div className="alert alert-danger">Could not invite user</div> );
        }
        return (
            <div className="organizer">
                <h2>{gettext("Pending invitations")}</h2>
                <PagedTable perPage={10} heading={heading}>
                    {invitationsRows}
                </PagedTable>
                <h3>{gettext('Invite facilitators')}</h3>
                <div className="form-group">
                    <input type="email" className="form-control" value={this.state.emailInput} onChange={this.handleChange} placeholder={gettext("Email address of user to invite")} />
                    <a className="btn btn-primary" onClick={this.handleInviteClick}>{gettext("Invite facilitator")}</a>
                </div>
                {errorMsg}
            </div>
        );
    }
}

InvitationList.propTypes = {
    invitations: React.PropTypes.array
}
