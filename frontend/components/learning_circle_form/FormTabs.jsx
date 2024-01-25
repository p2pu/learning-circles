import React from 'react'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import CourseSection from './CourseSection';
import LocationSection from './LocationSection';
import MeetingScheduler from './MeetingScheduler';
import CustomizeSection from './CustomizeSection';
import FinalizeSection from './FinalizeSection';

import 'react-tabs/style/react-tabs.css';
import 'p2pu-components/dist/build.css';


export default class FormTabs extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.switchTab = (tab) => this._switchTab(tab);
  }

  _switchTab(tab) {
    this.props.changeTab(tab)
  }

  render() {
    const hide = this.props.showHelp ? 'hide' : '';
    const {errors} = this.props;

    // map props.errors to tabs
    const tabFields = [
      ['course'],
      ['city', 'region', 'country', 'venue_name', 'venue_details', 'venue_address', 'language'],
      ['start_date', 'meeting_time', 'timezone'],
      ['name', 'description', 'course_description', 'signup_question', 'venue_website'],
      ['facilitator_goal', 'facilitator_concerns', 'facilitators'],
    ];
    const tabErrors = tabFields.map( tab => Object.keys(errors).filter(e => tab.indexOf(e) != -1));

    return (
      <div className='tabs-container'>
        <Tabs selectedIndex={this.props.currentTab} onSelect={this.switchTab} >
          <TabList className='tabs-list'>
            { this.props.allTabs.map( (tab,i) => <Tab key={i} className={'tabs-item' + (tabErrors[i].length?' error':'')}>{this.props.allTabs[i]}</Tab>) }
          </TabList>

          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 1: Select a Course *</h4>
              <CourseSection
                updateFormData={this.props.updateFormData}
                learningCircle={this.props.learningCircle}
                teamCourseList={this.props.teamCourseList}
                errors={this.props.errors}
                showHelp={this.props.showHelp}
                changeTab={this.props.changeTab}
              />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 2: Find a Location</h4>
              <LocationSection
                updateFormData={this.props.updateFormData}
                learningCircle={this.props.learningCircle}
                errors={this.props.errors}
              />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 3: Select Meeting Dates</h4>
              <MeetingScheduler
                updateFormData={this.props.updateFormData}
                learningCircle={this.props.learningCircle}
                errors={this.props.errors}
              />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 4: Customize</h4>
              <CustomizeSection
                updateFormData={this.props.updateFormData}
                learningCircle={this.props.learningCircle}
                errors={this.props.errors}
                showAlert={this.props.showAlert}
                tinymceScriptSrc={this.props.tinymceScriptSrc}
              />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 5: Finalize</h4>
              <FinalizeSection
                updateFormData={this.props.updateFormData}
                userId={this.props.userId}
                team={this.props.team}
                learningCircle={this.props.learningCircle}
                errors={this.props.errors}
              />
            </div>
          </TabPanel>
        </Tabs>
      </div>
    );
  }
}
