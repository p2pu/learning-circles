import React, { Component } from "react";
import axios from 'axios';
import AOS from 'aos';

import ResourceCard from './ResourceCard';
import { DISCOURSE_API_URL } from '../../helpers/constants';


export default class RecommendedResources extends Component {
  constructor(props) {
    super(props);
    this.state = {
      topics: []
    };
  }

  componentDidMount() {
    this.populateResources();
    AOS.init();
  }

  componentDidUpdate() {
    AOS.refresh();
  }

  populateResources = () => {
    const apiEndpoint = `${DISCOURSE_API_URL}/tags/c/learning-circles/facilitation/activity.json?order=views`;

    axios.get(apiEndpoint).then(res => {
      this.setState({ topics: res.data.topic_list.topics });
    });
  }

  render() {
    const top3topics = this.state.topics.slice(0,3);

    return (
      <div className="row resources">
        {
          top3topics.map((topic, index) => (
            <ResourceCard
              topic={topic}
              key={topic.id}
              defaultImagePath={'/static/images/learning-circle-default.jpg'}
              data-aos='fade-up'
              data-aos-delay={index * 100}
            />
          ))
        }
      </div>
    )
  }
}
