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
import EventsTable from './EventsTable';
import UpcomingLearningCirclesTable from './UpcomingLearningCirclesTable';
import CurrentLearningCirclesTable from './CurrentLearningCirclesTable';
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
    this.populateUpcomingEvents()
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

  populateUpcomingEvents = (params={}) => {
    // TODO - this doesn't make sense
    // let apiUrl = '/api/community_calendar/events/?format=json&user=self&limit=1'
    // fetch(apiUrl).then( resp => resp.json()).then( data => {
    //   this.setState({events: data.results});
    // });
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
    console.log(this.state.events)
    return (
      <div className="bg-light">
        <Alert
          show={this.state.alert.show}
          type={this.state.alert.type}
          closeAlert={this.closeAlert}>
          {this.state.alert.message}
        </Alert>
        <div className="row">
          <div className="col-12">
            <Title />
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
                  <p>You must be logged in to see your learning circles. <a className="p2pu-btn btn-dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                }
                {
                  this.state.user &&
                  <Tabs defaultIndex={0}>
                    <TabList>
                      <Tab><span className="minicaps bold text-xs">Upcoming</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Current</span></Tab>
                      <Tab><span className="minicaps bold text-xs">Completed</span></Tab>
                    </TabList>
                    <TabPanel>
                      <div data-aos='fade'>
                        <UpcomingLearningCirclesTable user={true} />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
                        <CurrentLearningCirclesTable user={true} />
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
                    <p>You must be logged in to see your team's learning circles. <a className="p2pu-btn btn-dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                  }
                  {
                    this.state.user &&
                    <Tabs defaultIndex={0}>
                      <TabList>
                        <Tab><span className="minicaps bold text-xs">Upcoming</span></Tab>
                        <Tab><span className="minicaps bold text-xs">Current</span></Tab>
                        <Tab><span className="minicaps bold text-xs">Completed</span></Tab>
                      </TabList>
                      <TabPanel>
                        <div data-aos='fade'>
                          <UpcomingLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
                        </div>
                      </TabPanel>
                      <TabPanel>
                        <div data-aos='fade'>
                          <CurrentLearningCirclesTable teamId={this.props.teamId} userIsOrganizer={this.props.userIsOrganizer} />
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
                  <div className="card-title">Team Members</div>
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
                            teamInvitationUrl={this.props.teamInvitationUrl}
                            createTeamInvitationUrl={this.props.createTeamInvitationUrl}
                            deleteTeamInvitationUrl={this.props.deleteTeamInvitationUrl}
                            teamMemberInvitationUrl={this.props.teamMemberInvitationUrl}
                            showAlert={this.showAlert}
                          />
                        </div>
                      </TabPanel>
                    </Tabs>
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
                      <p>You must be logged in to see your team's activity. <a className="p2pu-btn btn-dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
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
                <div className="card-title">My Courses</div>
                {
                  !this.state.user &&
                  <p>You must be logged in to see your courses. <a className="p2pu-btn btn-dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
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
                <div className="card-title">My Events</div>
                {
                  !this.state.user &&
                  <p>You must be logged in to see events you've added. <a className="p2pu-btn btn-dark btn-sm" href={"/en/login_redirect/"}>Log in or register</a></p>
                }
                {
                  this.state.user &&
                  <EventsTable />
                }
                <div className="">
                  <a className="p2pu-btn btn-sm dark" href="/en/community_calendar/event/add/">Add an event</a>
                </div>
                <div className="text-right">
                  <a href={"https://www.p2pu.org/en/events/"}>See all events</a>
                </div>
              </Card>
            </div>


            <div data-aos='fade'>
              <Card>
                <div className="card-title">Latest Discussion</div>
                <DiscourseTable />
                <div className="text-right">
                  <a href={"https://community.p2pu.org/"}>Go to the forum</a>
                </div>
              </Card>
            </div>

            <div data-aos='fade'>
              <Card>
                <div className="card-title">Activities for your Learning Circle</div>
                <RecommendedResources />
                <div className="text-right">
                  <a href={"https://community.p2pu.org/tags/activity/"}>See all activities</a>
                </div>
              </Card>
            </div>

          </div>

          <div className="col-12 col-lg-4">

            <div data-aos='fade'>
              <Card className="boston-banner">
                <div className="bold text-center text-white">Join us in Boston this September!</div>
                <div className="text-center mt-3">
                  <a href="https://boston2019.p2pu.org/" className="p2pu-btn light btn-sm">More info</a>
                </div>
              </Card>
            </div>

            <div data-aos='fade'>
              <Card className="bg-dark feedback-survey">
                <div className="bold text-center text-white">What do you think about your new learning circles dashboard?</div>
                <div className="text-center mt-3">
                  <a href="https://p2pu.typeform.com/to/WwRKql?first_impression=like" className="p2pu-btn light btn-sm">😍 I like it!</a>
                  <a href="https://p2pu.typeform.com/to/WwRKql?first_impression=dislike" className="p2pu-btn light btn-sm">😕 Meh</a>
                </div>
              </Card>
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
