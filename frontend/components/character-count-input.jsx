import React, { Component } from 'react'

export default class CharacterCountInput extends Component {
  constructor(props){
    super(props);
    this.state = {value: props.value}
    this.handleUpdate = this.handleUpdate.bind(this);
  }

  handleUpdate(e){
    this.setState({ value: e.currentTarget.value });
  }

  render() {
    return(
      <span>
        <input type="hidden" value={this.state.value} name={this.props.name} />
        <input 
          type="text"
          name="character_count_input"
          className={"textinput textInput form-control" + (this.props.error?' is-invalid':'')}
          value={this.state.value}
          onChange={this.handleUpdate}
        />
        <p>{this.state.value.length}/{this.props.maxLength}</p>
      </span>
    )
  }
}
