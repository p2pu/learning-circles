import React from 'react'
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import CourseSection from './CourseSection';
import LocationSection from './LocationSection';
import DayTimeSection from './DayTimeSection';
import CustomizeSection from './CustomizeSection';
import FinalizeSection from './FinalizeSection';
import 'react-tabs/style/react-tabs.css';

export default class FormTabs extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.switchTab = (tab) => this._switchTab(tab);
    this.updateFormData = (data) => this._updateFormData(data);
  }

  _switchTab(tab) {
    this.props.changeTab(tab)
  }

  render() {
    const hide = this.props.showHelp ? 'hide' : '';

    return (
      <div className='tabs-container'>
        <Tabs selectedIndex={this.props.currentTab} onSelect={this.switchTab} >
          <TabList className='tabs-list'>
            <Tab className='tabs-item'>{this.props.allTabs[0]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[1]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[2]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[3]}</Tab>
            <Tab className='tabs-item'>{this.props.allTabs[4]}</Tab>
          </TabList>

          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 1: Select a Course</h4>
              <CourseSection
                updateFormData={this.props.updateFormData}
                learningCircle={this.props.learningCircle}
                errors={this.props.errors}
                showHelp={this.props.showHelp}
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
              <h4>Step 3: Select the Day and Time</h4>
              <DayTimeSection
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
              />
            </div>
          </TabPanel>
          <TabPanel className='tab-content'>
            <div className='content-container'>
              <h4>Step 5: Finalize</h4>
              <FinalizeSection
                updateFormData={this.props.updateFormData}
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
