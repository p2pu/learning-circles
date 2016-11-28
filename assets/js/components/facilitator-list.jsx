import React from 'react'
import PagedTable from './paged-table'

require("./stylesheets/organizer-dash.scss");

export default class FacilitatorList extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            filterQuery: '',
            page: 0
        };
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e){
        this.setState({filterQuery: e.target.value});
    }

    render(){
        let re = new RegExp(this.state.filterQuery);
        let facilitators = this.props.facilitators.filter(f => 
            re.test(f.name + f.email)
        );
        let heading = <tr><th>Username</th><th>Email</th></tr>;
        let facilitatorRows = facilitators.sort(function(a,b){
            if (a.name < b.name) {
                return -1;
            }
            if (a.name > b.name) {
                return 1;
            }
            return 0;
        }).map(facil =>
            <tr key={facil.email}><td>{facil.name}</td><td>{facil.email}</td></tr>
        );
        return (
            <div className="organizer">
                <h2>Facilitators</h2>
                <div className="form-group">
                    <input type="text" className="form-control" value={this.state.filterQuery} onChange={this.handleChange} placeholder="Filter users by name or email" />
                </div>
                <PagedTable perPage={10} heading={heading}>{facilitatorRows}</PagedTable>
                <a>Invite facilitator</a>
            </div>
        );
    }
}

FacilitatorList.propTypes = {
    facilitators: React.PropTypes.array
}
