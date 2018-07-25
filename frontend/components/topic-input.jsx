import React, { Component } from 'react'
import {Creatable} from 'react-select'
import css from 'react-select/dist/react-select.css'

export default class TopicInput extends Component {
  constructor(props){
    super(props);
    let topics = [];
    if (props.value){
      topics = props.value.split(',').map(e => { return {label: e, value: e};});
    }
    this.state = {topics: topics}
    this.handleSelect = this.handleSelect.bind(this);
  }

  handleSelect(selected){
    const newTopicList = selected.map(option => option.value)
    this.setState({ topics: selected });
  }


  render(props) {
    const topicOptions = Array.from(this.props.topics);
    topicOptions.sort();

    return(
      <span>
        <input type="hidden" value={this.state.topics.map(t=>t.value).join(',')} name="topics" />
        <Creatable
          name="topics_input"
          multi={true}
          value={this.state.topics}
          onChange={this.handleSelect}
          options={topicOptions.map(topic => {
            return {
              value: topic,
              label: topic,
            };
          })}
        />
      </span>
    )
  }

}
