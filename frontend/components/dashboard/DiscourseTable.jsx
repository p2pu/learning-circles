import React, { Component } from "react";
import axios from "axios";
import AOS from 'aos';
import { DISCOURSE_API_URL } from "../../helpers/constants";


export default class DiscourseTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      topics: [],
      users: [],
      categories: [],
    };
    this.populateResources = () => this._populateResources();
    this.populateCategories = () => this._populateCategories();
  }

  componentDidMount() {
    this.populateResources();
    this.populateCategories();
    AOS.init();
  }

  componentDidUpdate() {
    AOS.refresh();
  }

  _populateResources() {
    const apiEndpoint = `${DISCOURSE_API_URL}/latest.json?order=created`;

    axios.get(apiEndpoint).then(res => {
      this.setState({ topics: res.data.topic_list.topics, users: res.data.users });
    });
  }

  _populateCategories() {
    const apiEndpoint = `${DISCOURSE_API_URL}/site.json`;

    axios.get(apiEndpoint).then(res => {
      this.setState({ categories: res.data.categories });
    });
  }

  render() {
    const top10topics = this.state.topics.slice(0,5);

    return (
      <div className="table-responsive" data-aos='fade'>
        <table className="table">
          <thead>
            <tr>
              <td>Topic</td>
              <td>Category</td>
              <td>Views</td>
            </tr>
          </thead>
          <tbody>
            {
              top10topics.map((topic, index) => {
                const category = this.state.categories.find(cat => cat.id == topic.category_id) || {};
                return(
                  <tr key={`${topic.slug}`}>
                    <td><a href={`${DISCOURSE_API_URL}/t/${ topic.slug }`}>{ topic.title }</a></td>
                    <td>{ category.name }</td>
                    <td>{ topic.views }</td>
                  </tr>
                )
              })
            }
          </tbody>
        </table>
      </div>
    );
  }
}
