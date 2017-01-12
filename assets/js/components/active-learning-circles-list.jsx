import React from 'react'
import PagedTable from './paged-table'
import moment from 'moment'

export default class ActiveLearningCircleList extends React.Component {

    render(){
        var heading = (
            <tr>
                <th>Details</th>
                <th>Signups</th>
                <th>Facilitator</th>
                <th>Next meeting</th>
                <th></th>
            </tr>
        );

        let learningCircleRows = this.props.learningCircles.map(lc => (
            <tr>
                <td>
                    { lc.course_title }<br/>
                    { lc.day }s, { lc.meeting_time } at { lc.venue_name }
                </td>
                <td>
                    { lc.signup_count }
                </td>
                <td>
                    { lc.facilitator.first_name } { lc.facilitator }
                </td>
                <td>
                    { moment(lc.next_meeting_date).format('ddd, D MMM') }
                </td>
                <td>
                    <a className="btn btn-primary" href={ lc.url }>View</a>
                </td>
            </tr>
        ));

        return (
            <div className="active-learning-circles-list">
                <h2>Active Learning Circles</h2>
                <PagedTable perPage={10} heading={heading}>{learningCircleRows}</PagedTable>
                <a href="/organize/studygroups/">View all learning circles</a>
            </div>
        );
    }
}


