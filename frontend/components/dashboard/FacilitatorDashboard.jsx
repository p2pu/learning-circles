import React from 'react';
import axios from 'axios';
import AOS from 'aos';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import Alert from '../learning_circle_form/Alert';
import Card from './Card';
import Notification from './Notification';
import DiscourseTable from './DiscourseTable';
import CoursesTable from './CoursesTable';
import UpcomingLearningCirclesTable from './UpcomingLearningCirclesTable';
import CurrentLearningCirclesTable from './CurrentLearningCirclesTable';
import CompletedLearningCirclesTable from './CompletedLearningCirclesTable';
import UpcomingMeetings from './UpcomingMeetings';
import RecommendedResources from "./RecommendedResources";
import GlobalSuccesses from "./GlobalSuccesses";
import InstagramFeed from "./InstagramFeed";
import Title from './Title';

import 'react-tabs/style/react-tabs.css';
import 'aos/dist/aos.css';
import '../stylesheets/dashboard.scss';


export default class FacilitatorDashboard extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      user: this.props.user,
      errors: {},
      alert: { show: false }
    };
    this.showAlert = (msg, type) => this._showAlert(msg, type);
    this.closeAlert = () => this._closeAlert();
  }

  componentDidMount(){
    AOS.init({
      duration: 500,
      delay: 100
    })
  }

  _showAlert(message, type) {
    this.setState({
      alert: {
        message,
        type,
        show: true
      }
    })
  }

  _closeAlert() {
    this.setState({ alert: { show: false }})
  }

  render() {
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
              <Notification level="warning">
                <p className="mb-0">Your email address has not yet been validated. Check your inbox for an email from us.</p>
                <a href={this.props.emailConfirmationUrl}>Re-send the validation email</a>
              </Notification>
            }

            {
              this.props.teamInvitationUrl &&
              <Notification level="success">
                <p className="mb-0">{`You've been invited to join ${this.props.teamName}. Do you want to join?`}</p>
                <a href={this.props.teamInvitationUrl}>Respond to this invitation</a>
              </Notification>
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
                        <UpcomingLearningCirclesTable />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
                        <CurrentLearningCirclesTable />
                      </div>
                    </TabPanel>
                    <TabPanel>
                      <div data-aos='fade'>
                        <CompletedLearningCirclesTable />
                      </div>
                    </TabPanel>
                  </Tabs>
                }
                <div className="text-right">
                  <a href={"/en/studygroup/create/"}>Start a learning circle</a>
                </div>
              </Card>
            </div>

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
                    <UpcomingMeetings scope="team" />
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
