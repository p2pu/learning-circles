import React from 'react';
import axios from 'axios';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';

import RegistrationModal from '../learning_circle_form/RegistrationModal';
import Alert from '../learning_circle_form/Alert';
import Card from './Card';
import DiscourseTable from './DiscourseTable';
import CoursesTable from './CoursesTable';
import UpcomingLearningCirclesTable from './UpcomingLearningCirclesTable';
import CurrentLearningCirclesTable from './CurrentLearningCirclesTable';
import CompletedLearningCirclesTable from './CompletedLearningCirclesTable';
import UpcomingMeetings from './UpcomingMeetings';
import RecommendedResources from "./RecommendedResources";
import Title from './Title';

import 'react-tabs/style/react-tabs.css';
import '../stylesheets/dashboard.scss';


export default class FacilitatorDashboard extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      user: this.props.user,
      errors: {},
      alert: { show: false },
      showModal: false,
    };
    this.showModal = () => this._showModal();
    this.closeModal = () => this._closeModal();
    this.showAlert = (msg, type) => this._showAlert(msg, type);
    this.closeAlert = () => this._closeAlert();
    this.registerUser = () => this._registerUser();
    this.onLogin = (user) => this._onLogin(user);
  }

  _showModal() {
    this.setState({ showModal: true })
  }

  _closeModal() {
    this.setState({ showModal: false })
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

  _onLogin(user) {
    this.setState({ user });
    this.showAlert("You're logged in! You can now save or publish your learning circle.", 'success')

    // TODO: remove this when we switch to the React component for the account in the navbar
    const accountLink = document.querySelector('nav .nav-items .account a');
    accountLink.setAttribute('href', '/en/accounts/logout');
    accountLink.innerText = 'Log out';
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
          <div className="col-8">
            <Card>
              <div className="card-title">My Learning Circles</div>
              <Tabs defaultIndex={0}>
                <TabList>
                  <Tab><span className="minicaps bold text-xs">Upcoming</span></Tab>
                  <Tab><span className="minicaps bold text-xs">Current</span></Tab>
                  <Tab><span className="minicaps bold text-xs">Completed</span></Tab>
                </TabList>
                <TabPanel>
                  <UpcomingLearningCirclesTable />
                </TabPanel>
                <TabPanel>
                  <CurrentLearningCirclesTable />
                </TabPanel>
                <TabPanel>
                  <CompletedLearningCirclesTable />
                </TabPanel>
              </Tabs>
            </Card>

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

            <Card>
              <div className="card-title">My Courses</div>
              <CoursesTable userEmail={this.state.user} />
              <div className="text-right">
                <a href={"https://www.p2pu.org/en/courses/"}>See all courses</a>
              </div>
            </Card>

            <Card>
              <div className="card-title">Latest Discussion</div>
              <DiscourseTable />
              <div className="text-right">
                <a href={"https://community.p2pu.org/"}>Go to the forum</a>
              </div>
            </Card>

            <Card>
              <div className="card-title">Recommended Resources</div>
              <RecommendedResources />
              <div className="text-right">
                <a href={"https://community.p2pu.org/c/learning-circles/"}>See all resources</a>
              </div>
            </Card>
          </div>

          <div className="col-4">
            <Card>
              <div className="card-title">Global Successes</div>
            </Card>

            <Card>
              <div className="card-title">Instagram</div>
            </Card>

            <Card className="bg-dark">
              <div className="bold text-center text-white">What do you think about your new learning circles dashboard?</div>
              <div className="text-center mt-3">
                <a href="#">
                  <button className="p2pu-btn light">😍 I like it!</button>
                </a>
                <a href="#">
                  <button className="p2pu-btn light">😕 Meh</button>
                </a>
              </div>
            </Card>
          </div>
        </div>
        <RegistrationModal
          open={this.state.showModal}
          closeModal={this.closeModal}
          user={this.props.user}
          onLogin={this.onLogin}
          showAlert={this.showAlert}
        />
      </div>
    );
  }
}
