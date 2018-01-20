import React from 'react'
import FormTabs from './form-tabs'
import HelpSection from './help-section'
import ActionBar from './action-bar'

export default class CreateLearningCircleForm extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.nextTab = () => this._nextTab();
    this.generateAction = () => this._generateAction()
  }

  _nextTab() {
    this.props.changeTab(this.props.currentTab + 1)
  }

  _generateAction() {
    if (this.props.currentTab === 3) {
      return(
        <button className="p2pu-btn orange" onClick={this.props.onSubmitForm}>
          Save and Publish
        </button>
      )
    }

    return(
      <button className="p2pu-btn blue" onClick={this.nextTab}>
        Next Step<i className="fa fa-arrow-right" aria-hidden="true"></i>
      </button>
    )
  }

  render() {
    return (
      <div className='action-bar'>
        <button onClick={this.props.onCancel} className="p2pu-btn transparent">Cancel</button>
        <button onClick={this.props.onSaveDraft} className="p2pu-btn dark">Save Draft</button>
        { this.generateAction() }
      </div>
    );
  }
}
