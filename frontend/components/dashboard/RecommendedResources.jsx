import React, { Component } from "react";
import axios from 'axios';

import ResourceCard from './ResourceCard';
import { DISCOURSE_API_URL } from '../../helpers/constants';


export default class RecommendedResources extends Component {
  constructor(props) {
    super(props);
    this.state = {
      topics: []
    };
    this.populateResources = () => this._populateResources();
  }

  componentDidMount() {
    this.populateResources();
  }

  _populateResources() {
    const apiEndpoint = `${DISCOURSE_API_URL}/c/learning-circles/facilitation.json?tags=featured`;

    axios.get(apiEndpoint).then(res => {
      this.setState({ topics: res.data.topic_list.topics });
    });
  }

  render() {

    return (
      <div className="row resources">
        {
          this.state.topics.map(topic => (
            <ResourceCard topic={topic} key={topic.id} defaultImagePath={'/static/images/learning-circle-default.jpg'} />
          ))
        }
      </div>
    )
  }
}
