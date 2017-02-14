import React from 'react'
import TabSelector from './tab-selector'
import MeetingCalendar from './meeting-calendar'
import WeeklyMeetingsList from './weekly-meetings-list'
import FacilitatorList from './facilitator-list'
import ActiveLearningCirclesList from './active-learning-circles-list'

require("./stylesheets/organizer-dash.scss");

export default class OrganizerDash extends React.Component{
    render() {
        return (
            <div className="organizer-dash">
                <h1>{gettext("Organizer Dashboard")}</h1>
                <TabSelector header={[gettext('Upcoming Meetings'), gettext('Active Learning Circles'), gettext('Facilitators')]} >
                    <WeeklyMeetingsList
                        meetings={this.props.meetings} 
                        learningCircles={this.props.activeLearningCircles} />
                    <ActiveLearningCirclesList 
                        learningCircles={this.props.activeLearningCircles} />
                    <FacilitatorList facilitators={this.props.facilitators} />

                </TabSelector>
            </div>
        );
    }
}
