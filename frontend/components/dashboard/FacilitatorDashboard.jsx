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
      <div className="container-fluid">
        <Alert
          show={this.state.alert.show}
          type={this.state.alert.type}
          closeAlert={this.closeAlert}>
          {this.state.alert.message}
        </Alert>
        <div className="row">
          <div className="col-12">
            <Title user={this.state.user} userData={this.props.userData} />
          </div>
        </div>

        <div className="row">
          <div className="col-12 col-lg-8">
            <div data-aos='fade'>
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

            <div data-aos='fade'>
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
                      <div data-aos='fade'>
                        <ActiveLearningCirclesTable user={true} />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
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

            {
              this.props.teamId &&
              <div data-aos='fade'>
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
                        <div data-aos='fade'>
                          <ActiveLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
                        </div>
                      </TabPanel>
                      <TabPanel>
                        <div data-aos='fade'>
                          <CompletedLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
                        </div>
                      </TabPanel>
                    </Tabs>
                  }
                  <div className="text-right">
                    <a href={"https://www.p2pu.org/en/teams/"}>See all teams</a>
                  </div>
                </Card>
              </div>
            }

            {
              this.props.userIsOrganizer &&
              <div data-aos='fade'>
                <Card>
                  <div className="card-title">Team Management</div>
                  <Tabs defaultIndex={0}>
                    <TabList>
                      <Tab><span className="minicaps bold text-xs">Team members</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Pending invitations</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Invite new members</span></Tab>
                    </TabList>
                    <TabPanel>
                      <div data-aos='fade'>
                        <TeamMembersTable teamId={this.props.teamId} />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
                        <TeamInvitationsTable teamId={this.props.teamId} />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
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


            <div data-aos='fade'>
              <Card>
                <div className="card-title">What's Happening This Week</div>
                <Tabs defaultIndex={0}>
                  <TabList>
                    <Tab><span className="minicaps bold text-xs">Globally</span></Tab>
                    <Tab><span className="minicaps bold text-xs">My Team</span></Tab>
                  </TabList>
                  <TabPanel>
                    <UpcomingMeetings scope="global" />
                  </TabPanel>
                  <TabPanel>
                    {
                      this.state.user ?
                      <UpcomingMeetings scope="team" /> :
                      <p>You must be logged in to see your team's activity. <a className="p2pu-btn btn dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                    }
                  </TabPanel>
                </Tabs>
                <div className="text-right">
                  <a href={"https://www.p2pu.org/en/learning-circles/"}>See all learning circles</a>
                </div>
              </Card>
            </div>

            <div data-aos='fade'>
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

            <div data-aos='fade'>
              <Card>
                <div className="card-title">Community Events</div>
                <DiscourseTable endpoint={'/c/community-events.json?order=created'} />
                <div className="text-right">
                  <a href={"https://community.p2pu.org/c/community-events/"}>See all events</a>
                </div>
              </Card>
            </div>


            <div data-aos='fade'>
              <Card>
                <div className="card-title">Latest Discussion</div>
                <DiscourseTable endpoint={'/latest.json?order=created'} />
                <div className="text-right">
                  <a href={"https://community.p2pu.org/"}>Go to the forum</a>
                </div>
              </Card>
            </div>

            <div data-aos='fade'>
              <Card>
                <div className="card-title">Facilitator Resources</div>
                <RecommendedResources />
                <div className="text-right">
                  <a href={"https://www.p2pu.org/en/facilitate/"}>See all resources</a>
                </div>
              </Card>
            </div>
          </div>

          <div className="col-12 col-lg-4">
            <div data-aos="fade">
              <FacilitatorProfile facilitator={this.props.userData} themeColor={"blue"} />
            </div>
            <div data-aos='fade'>
              <Announcements />
            </div>

            <div data-aos='fade'>
              <Card>
                <div className="card-title">Recent Successes</div>
                <GlobalSuccesses />
              </Card>
            </div>

            <div data-aos='fade'>
              <Card>
                <div className="card-title">Latest Posts on Instagram</div>
                <InstagramFeed />
              </Card>
            </div>

          </div>
        </div>
      </div>
    );
  }
}
