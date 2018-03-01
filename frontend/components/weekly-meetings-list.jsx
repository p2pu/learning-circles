import React from 'react'
import moment from 'moment'

class MeetingRow extends React.Component {
    render() {
        const {meeting, learningCircles} = this.props;
        let rsvp = null;
        if (meeting.rsvp) {
            rsvp = (<span>{gettext("Yes")} ({meeting.rsvp.yes}), {gettext("No")} ({meeting.rsvp.no})</span>);
        }
        let feedback = null;
        if (meeting.feedback) {
            feedback = (<a href={meeting.feedback.url}>{gettext("View feedback")}</a>);
        }
        return (
            <tr>
                <td>{meeting.study_group.course_title} - {gettext("week")} {meeting.meeting_number}</td>
                <td>{meeting.study_group.facilitator}</td>
                <td>{moment(meeting.meeting_date + ' ' + meeting.meeting_time).format('H:mm') + ' ' + meeting.study_group.timezone_display}</td>
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
            meetingNodes.push(<tr><td colSpan={5}>{gettext("No meetings")}</td></tr>);
        }

        return (
            <div className="weekly-meeting-list">
                <h3>{day.format('ddd, D MMM')}</h3>
                <table>
                    <thead>
                        <tr>
                            <th>{gettext("Details")}</th>
                            <th>{gettext("Facilitator")}</th>
                            <th>{gettext("Time")}</th>
                            <th>{gettext("RSVPs")}</th>
                            <th>{gettext("Feedback")}</th>
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
        const nextWeek = moment(weekStart).add(1, 'week');
        const showNextWeek = moment().startOf('week').add(2, 'week').isSameOrAfter(nextWeek);
        const prevWeek = moment(weekStart).subtract(1, 'week');
        const showPrevWeek = moment().startOf('week').subtract(2, 'week').isSameOrBefore(prevWeek);
        return (
            <div>
                <h2>{interpolate(gettext("Upcoming meetings Week of %s"), [weekStart.format('MMM. D, YYYY')])}</h2>
                <a className="btn btn-primary" disabled={!showPrevWeek} onClick={e=> this._handleWeekChange(prevWeek) }>{interpolate(gettext("Week of %s"), [prevWeek.format('MMM. D, YYYY')])}</a>&nbsp;
                <a className="btn btn-primary" disabled={!showNextWeek} onClick={e=> this._handleWeekChange(nextWeek) }>{interpolate(gettext("Week of %s"), [nextWeek.format('MMM. D, YYYY')])}</a>&nbsp;
                <a className="btn btn-primary" onClick={e=> this._handleWeekChange(moment().startOf('week')) }>{gettext("This week")}</a>
                { week.map(day => <DayMeetingTable day={day} {...this.props} />) }
                <p><a href="/organize/studygroup_meetings/">{gettext("View all meetings")}</a></p>
            </div>
        );
    }
}
