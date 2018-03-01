import React from 'react'
import { Step1, Step2, Step3, Step4, Step5 } from './HelpText'


export default class CreateLearningCircleForm extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
    this.renderHelpText = () => this._renderHelpText();
  }

  _renderHelpText() {
    switch (this.props.currentTab) {
      case 0:
        return Step1();
      case 1:
        return Step2();
      case 2:
        return Step3();
      case 3:
        return Step4();
      case 4:
        return Step5();
    }
  }

  render() {
    return (
      <div className='help-container'>
        { this.renderHelpText() }
      </div>
    );
  }
}
