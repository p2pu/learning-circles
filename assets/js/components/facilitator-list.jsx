import React from 'react'

require("./stylesheets/organizer-dash.scss");

export default class FacilitatorList extends React.Component {
    constructor(props){
        super(props);
        this.state = {filterQuery: ''};
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e){
        this.setState({filterQuery: e.target.value});
    }

    render(){
        let re = new RegExp(this.state.filterQuery);
        let facilitators = this.props.facilitators.filter((f) => 
                re.test(f.name + f.email));
        let facilitatorRows = facilitators.map(function(facil){
            return (<li key={facil.email}> {facil.name}: {facil.email} </li>);
        });
        return (
            <div className="organizer">
                <h2>Facilitators</h2>
                <input type="text" value={this.state.filterQuery} onChange={this.handleChange}/>
                <ul>{facilitatorRows}</ul>
                <a>Invite facilitator</a>
            </div>
        );
    }
}

FacilitatorList.propTypes = {
    facilitators: React.PropTypes.array
}
