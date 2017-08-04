import React from 'react'
import TabSelector from './tab-selector'
import WeeklyMeetingsList from './weekly-meetings-list'
import ActiveLearningCirclesList from './active-learning-circles-list'
import FacilitatorList from './facilitator-list'
import InvitationList from './invitation-list'

require("./stylesheets/organizer-dash.scss");

export default class OrganizerDash extends React.Component{
    render() {
        return (
            <div className="organizer-dash">
                <h1>{gettext("Organizer Dashboard")}</h1>
                <TabSelector header={[gettext('Upcoming Meetings'), gettext('Active Learning Circles'), gettext('Facilitators'), gettext('Invitations')]} >
                    <WeeklyMeetingsList
                        meetings={this.props.meetings} 
                        learningCircles={this.props.activeLearningCircles} />
                    <ActiveLearningCirclesList 
                        learningCircles={this.props.activeLearningCircles} />
                    <FacilitatorList facilitators={this.props.facilitators} />
                    <InvitationList
                        teamInviteUrl={this.props.teamInviteUrl}
                        invitations={this.props.invitations} />
                </TabSelector>
            </div>
        );
    }
}
