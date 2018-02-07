import React from 'react'
import FormTabs from './FormTabs'
import ActionBar from './ActionBar'

export default class FormContainer extends React.Component{
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
    const hide = this.props.showHelp ? 'show-help' : 'hide-help';

    return (
      <div className={`form-container ${hide}`}>
        <FormTabs { ...this.props } />
        <ActionBar { ...this.props} />
      </div>
    );
  }
}
