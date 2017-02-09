import React from 'react'
import PagedTable from './paged-table'

require("./stylesheets/facilitator-list.scss");

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
        let re = new RegExp(this.state.filterQuery, 'i');
        let facilitators = this.props.facilitators.filter(f => 
            re.test(f.name + f.email)
        );
        let heading = <tr><th>{gettext("Name")}</th><th>{gettext("Email")}</th></tr>;
        let facilitatorRows = facilitators.sort(function(a,b){
            if (a.name.toLowerCase() < b.name.toLowerCase()) {
                return -1;
            }
            if (a.name.toLowerCase() > b.name.toLowerCase()) {
                return 1;
            }
            return 0;
        }).map(facil =>
            <tr key={facil.email}><td>{facil.name}</td><td>{facil.email}</td></tr>
        );
        return (
            <div className="organizer">
                <h2>{gettext("Facilitators")}</h2>
                <div className="form-group">
                    <input type="text" className="form-control" value={this.state.filterQuery} onChange={this.handleChange} placeholder={gettext("Filter users by name or email")} />
                </div>
                <PagedTable perPage={10} heading={heading}>{facilitatorRows}</PagedTable>
            </div>
        );
    }
}

FacilitatorList.propTypes = {
    facilitators: React.PropTypes.array
}
