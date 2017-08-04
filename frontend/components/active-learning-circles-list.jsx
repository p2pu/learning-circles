import React from 'react'
import PagedTable from './paged-table'
import moment from 'moment'

export default class ActiveLearningCircleList extends React.Component {

    render(){
        var heading = (
            <tr>
                <th>{gettext("Details")}</th>
                <th>{gettext("Signups")}</th>
                <th>{gettext("Facilitator")}</th>
                <th>{gettext("Next meeting")}</th>
                <th></th>
            </tr>
        );

        let learningCircleRows = this.props.learningCircles.map(lc => (
            <tr>
                <td>
                    { lc.course_title }<br/>
                    { lc.day }s, { lc.meeting_time } {gettext("at")} { lc.venue }
                </td>
                <td>
                    { lc.signup_count }
                </td>
                <td>
                    { lc.facilitator.first_name } { lc.facilitator }
                </td>
                <td>
                    { lc.next_meeting_date && moment(lc.next_meeting_date).format('ddd, D MMM') }
                </td>
                <td>
                    <a className="btn btn-primary" href={ lc.url }>{gettext("View")}</a>
                </td>
            </tr>
        ));

        return (
            <div className="active-learning-circles-list">
                <h2>{gettext("Active Learning Circles")}</h2>
                <PagedTable perPage={10} heading={heading}>{learningCircleRows}</PagedTable>
                <a href="/organize/studygroups/">{gettext("View all learning circles")}</a>
            </div>
        );
    }
}


