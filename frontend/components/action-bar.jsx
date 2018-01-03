import React from 'react'
import FormTabs from './form-tabs'
import HelpSection from './help-section'
import ActionBar from './action-bar'

export default class CreateLearningCircleForm extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.nextTab = () => this._nextTab();
  }

  _nextTab() {
    this.props.changeTab(this.props.currentTab + 1)
  }

  render() {
    return (
      <div className='action-bar'>
        <button className="p2pu-btn transparent">Cancel</button>
        <button className="p2pu-btn dark">Save Draft</button>
        <button className="p2pu-btn blue" onClick={this.nextTab}>
          Next Step<i className="fa fa-arrow-right" aria-hidden="true"></i>
        </button>
      </div>
    );
  }
}
