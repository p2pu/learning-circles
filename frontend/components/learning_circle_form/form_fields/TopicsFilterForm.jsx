import React, { Component } from 'react'
import CheckboxWithLabel from '../../common/CheckboxWithLabel'
import SelectWithLabel from '../../common/SelectWithLabel'
import css from 'react-select/dist/react-select.css'
import { COURSE_CATEGORIES } from '../../../constants'
import ApiHelper from '../../../helpers/ApiHelper'
import { keys } from 'lodash'

export default class TopicsFilterForm extends Component {
  constructor(props) {
    super(props)
    this.state = { options: [] };
    this.mapArrayToSelectOptions = (arr) => this._mapArrayToSelectOptions(arr);
    this.extractTopicsArray = (opts) => this._extractTopicsArray(opts);
    this.handleSelect = (selected) => this._handleSelect(selected);
    this.fetchTopics = () => this._fetchTopics();
  }

  componentDidMount() {
    this.fetchTopics();
  }

  componentWillReceiveProps(nextProps) {
    if (this.props !== nextProps) {
      const topics = nextProps.topics ? nextProps.topics.map((topic) => ({ value: topic, label: topic })) : [];
      this.setState({ topics: topics })
    }
  }

  _fetchTopics() {
    const resourceType = `${this.props.searchSubject}Topics`;
    const api = new ApiHelper(resourceType);
    const params = {};
    const callback = (response) => {
      const topics = keys(response.topics).sort()
      const options = this.mapArrayToSelectOptions(topics);
      this.setState({ options })
    }

    api.fetchResource({ params, callback })
  }

  _handleSelect(selected) {
    const newTopicList = this.extractTopicsArray(selected);
    this.props.updateQueryParams({ topics: newTopicList })
  }

  _mapArrayToSelectOptions(array) {
    return array.map((topic) => ({ value: topic, label: topic }))
  }

  _extractTopicsArray(options) {
    return options.map(option => option.value)
  }

  render() {
    const value = this.mapArrayToSelectOptions(this.props.topics || []);

    return(
      <div className="col-sm-12">
        <SelectWithLabel
          label='What topics are you interested in?'
          classes='no-flex'
          options={this.state.options}
          multi={true}
          value={value}
          onChange={this.handleSelect}
          placeholder='Select as many topics as you want'
        />
      </div>
    )
  }
}
