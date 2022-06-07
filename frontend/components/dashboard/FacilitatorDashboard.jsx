import React from 'react';
import axios from 'axios';
import AOS from 'aos';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import ApiHelper from "../../helpers/ApiHelper";
import Alert from '../learning_circle_form/Alert';
import Card from './Card';
import Notification from './Notification';
import DiscourseTable from './DiscourseTable';
import CoursesTable from './CoursesTable';
import MemberLearningCirclesTable from './MemberLearningCirclesTable';
import UpcomingLearningCirclesTable from './UpcomingLearningCirclesTable';
import CurrentLearningCirclesTable from './CurrentLearningCirclesTable';
import ActiveLearningCirclesTable from './ActiveLearningCirclesTable';
import CompletedLearningCirclesTable from './CompletedLearningCirclesTable';
import UpcomingMeetings from './UpcomingMeetings';
import RecommendedResources from "./RecommendedResources";
import GlobalSuccesses from "./GlobalSuccesses";
import InstagramFeed from "./InstagramFeed";
import Title from './Title';
import EmailValidationNotification from './EmailValidationNotification'
import TeamInvitationNotification from './TeamInvitationNotification'
import UpcomingEventNotification from './UpcomingEventNotification'
import TeamMembersTable from './TeamMembersTable'
import TeamInvitationsTable from './TeamInvitationsTable'
import OrganizerTeamInvitations from './OrganizerTeamInvitations'
import FacilitatorProfile from './FacilitatorProfile'
import Announcements from './Announcements'

import 'react-tabs/style/react-tabs.css';
import 'aos/dist/aos.css';
import '../stylesheets/dashboard.scss';


export default class FacilitatorDashboard extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      user: this.props.user,
      errors: {},
      alert: { show: false },
      invitationNotifications: [],
      events: [],
    };
  }

  componentDidMount(){
    this.populateInvitationNotifications()
    AOS.init({
      duration: 500,
      delay: 100
    })
  }

  populateInvitationNotifications = (params={}) => {
    const api = new ApiHelper('invitationNotifications');

    const onSuccess = (data) => {
      this.setState({ invitationNotifications: data.items })
    }

    api.fetchResource({ callback: onSuccess, params: {} })
  }

  showAlert = (message, type) => {
    this.setState({
      alert: {
        message,
        type,
        show: true
      }
    })
  }

  closeAlert = () => {
    this.setState({ alert: { show: false }})
  }

  render() {
    return (
      <div className="container">
        <Alert
          show={this.state.alert.show}
          type={this.state.alert.type}
          closeAlert={this.closeAlert}>
          {this.state.alert.message}
        </Alert>
        <div className="row">
          <div className="col-12">
            <Title user={this.state.user} userData={this.props.userData} />

            <div>
            {
              this.props.emailConfirmationUrl &&
              <EmailValidationNotification emailConfirmationUrl={this.props.emailConfirmationUrl} showAlert={this.showAlert} />
            }

            {
              this.state.invitationNotifications.map((invitation, i) => {
                return (<TeamInvitationNotification
                  key={`invitatation-${i}`}
                  invitation={invitation}
                />)
              })
            }
            </div>

            <Announcements />

            <RecommendedResources 
              isMemberTeam={this.props.isMemberTeam}
              isStaff={this.props.isStaff}
              memberSupportUrl={this.props.memberSupportUrl}
            />

            { (this.props.isMemberTeam || this.props.isStaff) &&
              <Card>
                <div className="card-title">Member Learning Circles</div>
                <MemberLearningCirclesTable />
              </Card>
            }

            <div>
              <Card>
                <div className="card-title">My Learning Circles</div>
                {
                  !this.state.user &&
                  <p>You must be logged in to see your learning circles. <a className="p2pu-btn btn dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                }
                {
                  this.state.user &&
                  <Tabs defaultIndex={0}>
                    <TabList>
                      <Tab><span className="minicaps bold text-xs">Active & Upcoming</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Completed</span></Tab>
                    </TabList>
                    <TabPanel>
                      <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                        <ActiveLearningCirclesTable user={true} />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                        <CompletedLearningCirclesTable user={true} />
                      </div>
                    </TabPanel>
                  </Tabs>
                }
                <div className="text-right">
                  <a href={"/en/studygroup/create/"}>Start a learning circle</a>
                </div>
              </Card>
            </div>

            <div>
              <Card>
                <div className="card-title">Courses I've Added</div>
                {
                  !this.state.user &&
                  <p>You must be logged in to see your courses. <a className="p2pu-btn btn dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                }
                {
                  this.state.user &&
                  <CoursesTable userEmail={this.state.user} />
                }
                <div className="text-right">
                  <a href={"https://www.p2pu.org/en/courses/"}>See all courses</a>
                </div>
              </Card>
            </div>

            {
              this.props.teamId &&
              <div>
                <Card>
                  <div className="card-title">My Team's Learning Circles</div>
                  {
                    !this.state.user &&
                    <p>You must be logged in to see your team's learning circles. <a className="p2pu-btn btn dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                  }
                  {
                    this.state.user &&
                    <Tabs defaultIndex={0}>
                      <TabList>
                        <Tab><span className="minicaps bold text-xs">Active & Upcoming</span></Tab>
                        <Tab><span className="minicaps bold text-xs">Completed</span></Tab>
                      </TabList>
                      <TabPanel>
                        <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                          <ActiveLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
                        </div>
                      </TabPanel>
                      <TabPanel>
                        <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                          <CompletedLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
                        </div>
                      </TabPanel>
                    </Tabs>
                  }
                </Card>
              </div>
            }

            {
              this.props.userIsOrganizer &&
              <div>
                <Card>
                  <div className="card-title">Team Management</div>
                  <Tabs defaultIndex={0}>
                    <TabList>
                      <Tab><span className="minicaps bold text-xs">Team members</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Pending invitations</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Invite new members</span></Tab>
                    </TabList>
                    <TabPanel>
                      <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                        <TeamMembersTable 
                          teamId={this.props.teamId}
                          deleteTeamMembershipApiUrl={this.props.deleteTeamMembershipApiUrl}
                        />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                        <TeamInvitationsTable 
                          teamId={this.props.teamId} 
                          deleteTeamInvitationApiUrl={this.props.deleteTeamInvitationApiUrl}
                        />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade' data-aos-anchor-placement="top-bottom">
                        <OrganizerTeamInvitations
                          teamInvitationLink={this.props.teamInvitationLink}
                          createTeamInvitationLink={this.props.createTeamInvitationLink}
                          deleteTeamInvitationLink={this.props.deleteTeamInvitationLink}
                          teamMemberInvitationUrl={this.props.teamMemberInvitationUrl}
                          showAlert={this.showAlert}
                        />
                      </div>
                    </TabPanel>
                  </Tabs>
                  <div className="text-right">
                    <a href={this.props.editTeamUrl}>Edit team information</a>
                  </div>
                </Card>
              </div>
            }

            <div>
              <Card>
                <div className="card-title">Latest Discussion</div>
                <DiscourseTable endpoint={'/latest.json?order=created'} />
                <div className="text-right">
                  <a href={"https://community.p2pu.org/"}>Go to the forum</a>
                </div>
              </Card>
            </div>

          </div>
        </div>
      </div>
    );
  }
}
