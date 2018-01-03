import React from 'react'
import FormTabs from './form-tabs'
import HelpSection from './help-section'
import ActionBar from './action-bar'

import './stylesheets/learning-circle-form.scss'

export default class CreateLearningCircleForm extends React.Component{

  constructor(props){
    super(props);
    this.state = { currentTab: 0, showHelp: true };
    this.changeTab = (tab) => this._changeTab(tab);
    this.toggleHelp = () => this._toggleHelp();
    this.allTabs = {
      0: '1. Course',
      1: '2. Location',
      2: '3. Day & Time',
      3: '4. Finalize'
    };
  }

  _toggleHelp() {
    this.setState({ showHelp: !this.state.showHelp })
  }

  _changeTab(tab) {
    if (!!this.allTabs[tab]) {
      this.setState({ currentTab: tab })
    } else {
      this.setState({ currentTab: 0 })
    }
  }

  render() {
    return (
      <div className='page-container'>
        <FormTabs showHelp={this.state.showHelp} toggleHelp={this.toggleHelp} currentTab={this.state.currentTab} allTabs={this.allTabs} changeTab={this.changeTab} />
        <HelpSection currentTab={this.state.currentTab} open={this.state.openHelp} />
        <ActionBar currentTab={this.state.currentTab} changeTab={this.changeTab} />
      </div>
    );
  }
}
