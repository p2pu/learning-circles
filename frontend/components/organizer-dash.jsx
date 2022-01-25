import React from 'react'
import TabSelector from './tab-selector'
import WeeklyMeetingsList from './weekly-meetings-list'
import ActiveLearningCirclesList from './active-learning-circles-list'

require("./stylesheets/organizer-dash.scss");

export default class OrganizerDash extends React.Component{
    render() {
        return (
            <div className="organizer-dash">
                <h1>{gettext("Organizer Dashboard")}</h1>
                <TabSelector header={[gettext('Upcoming Meetings'), gettext('Active Learning Circles')]} >
                    <WeeklyMeetingsList
                        meetings={this.props.meetings} 
                        learningCircles={this.props.activeLearningCircles} />
                    <ActiveLearningCirclesList 
                        learningCircles={this.props.activeLearningCircles} />
                </TabSelector>
            </div>
        );
    }
}
