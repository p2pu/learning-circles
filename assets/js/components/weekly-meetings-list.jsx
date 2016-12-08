import React from 'react'
import moment from 'moment'

class MeetingRow extends React.Component {
    render() {
        const {meeting, learningCircles} = this.props;
        let rsvp = null;
        if (meeting.rsvp) {
            rsvp = (<span>Yes ({meeting.rsvp.yes}), No ({meeting.rsvp.no})</span>);
        }
        let feedback = null;
        if (meeting.feedback) {
            feedback = (<a href={meeting.feedback.url}>View feedback</a>);
        }
        return (
            <tr>
                <td>{meeting.study_group.course_title}</td>
                <td>{meeting.study_group.facilitator}</td>
                <td>{moment(meeting.meeting_date + ' ' + meeting.meeting_time).format('H:mm') + ' ' + meeting.study_group.time_zone}</td>
                <td>{rsvp}</td>
                <td>{feedback}</td>
            </tr>
        );
    }
}

class DayMeetingTable extends React.Component {
    render(){
        const {meetings, day} = this.props;

        let meetingNodes = meetings.filter(m => 
            day.isSame(m.meeting_date, 'day')
        ).map(m => <MeetingRow meeting={m} {...this.props} />);

        if (meetingNodes.length == 0) {
            meetingNodes.push(<tr><td colSpan={5}>No meetings</td></tr>);
        }

        return (
            <div className="weekly-meeting-list">
                <h3>{day.format('ddd, D MMM')}</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Details</th>
                            <th>Facilitator</th>
                            <th>Time</th>
                            <th>RSVPs</th>
                            <th>Feedback</th>
                        </tr>
                    </thead>
                     <tbody>
                        {meetingNodes}
                     </tbody>
                </table>
            </div>
        );
    }
}

export default class WeeklyMeetingsList extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            weekStart: moment().startOf('week')
        };
        this._handleWeekChange = this._handleWeekChange.bind(this);
    }

    _handleWeekChange(week){
        this.setState({weekStart: week});
    }

    render(){
        const {meetings} = this.props;
        const {weekStart} = this.state;
        let week = [];
        for (let i=0; i<7; ++i) {
            week.push(moment(weekStart).add(i, 'days'));
        }
        let times = meetings.filter(
            m => weekStart.isSame(m.meeting_date, 'week')
        ).map(
            m => m.meeting_time
        );
        return (
            <div>
                <h2>Upcoming meetings Week of {weekStart.format('MMM. D, YYYY')}</h2>
                <a className="btn btn-primary" onClick={e=> this._handleWeekChange(this.state.weekStart.subtract(1, 'week')) }>Previous week</a>&nbsp;
                <a className="btn btn-primary" onClick={e=> this._handleWeekChange(this.state.weekStart.add(1, 'week')) }>Next week</a>&nbsp;
                <a className="btn btn-primary" onClick={e=> this._handleWeekChange(moment().startOf('week')) }>This week</a>
                { week.map(day => <DayMeetingTable day={day} {...this.props} />) }
                <p><a href="/organize/studygroup_meetings/">View all meetings</a></p>
            </div>
        );
    }
}
