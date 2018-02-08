import React, { Component } from 'react'

export default class SwitchWithLabels extends Component {
  constructor(props) {
    super(props)
    this.state = { checked: this.props.defaultChecked }
    this.handleChange = (event) => this._handleChange(event);
    this.handleClickLabel = (value) => this._handleClickLabel(value);
    this.handleChange = (event) => this._handleChange(event);
  }

  _handleChange(event) {
    const checked = event.currentTarget.checked;

    this.setState({ checked }, this.props.onChange(checked));
  }

  _handleClickLabel(value) {
    return () => { this.setState({ checked: value }, this.props.onChange(value)) };
  }

  render() {
    return(
      <div className="switch-container">
        <span onClick={this.handleClickLabel(false)}>{ this.props.labelLeft }</span>
        <label>
          <input
            checked={ this.state.checked }
            onChange={ this.handleChange }
            className="switch"
            type="checkbox"
          />
          <div className="switch-background">
            <div className="switch-button"></div>
          </div>
        </label>
        <span onClick={this.handleClickLabel(true)}>{ this.props.labelRight }</span>
      </div>
    );
  }
}

