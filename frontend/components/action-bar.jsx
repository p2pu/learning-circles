import React from 'react'
import FormTabs from './form-tabs'
import HelpSection from './help-section'
import ActionBar from './action-bar'

export default class CreateLearningCircleForm extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.nextTab = () => this._nextTab();
    this.prevTab = () => this._prevTab();
    this.generateNextAction = () => this._generateNextAction()
    this.generatePreviousAction = () => this._generatePreviousAction()
  }

  _nextTab() {
    this.props.changeTab(this.props.currentTab + 1)
  }

  _prevTab() {
    this.props.changeTab(this.props.currentTab - 1)
  }

  _generateNextAction() {
    if (this.props.currentTab === 3) {
      return(
        <button className="p2pu-btn orange" onClick={this.props.onSubmitForm}>
          Publish
        </button>
      )
    }

    return(
      <button className="p2pu-btn blue" onClick={this.nextTab}>
        Next Step<i className="fa fa-arrow-right" aria-hidden="true"></i>
      </button>
    )
  }

  _generatePreviousAction() {
    if (this.props.currentTab === 0) {
      return null
    }

    return(
      <button className="p2pu-btn blue" onClick={this.prevTab}>
        <i className="fa fa-arrow-left" aria-hidden="true"></i>Previous Step
      </button>
    )
  }

  render() {
    return (
      <div className='action-bar'>
        { this.generatePreviousAction() }
        <button onClick={this.props.onCancel} className="p2pu-btn transparent">Cancel</button>
        <button onClick={this.props.onSaveDraft} className="p2pu-btn dark">Save Draft</button>
        { this.generateNextAction() }
      </div>
    );
  }
}
