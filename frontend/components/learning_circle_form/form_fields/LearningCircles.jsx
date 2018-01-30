import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import SearchForm from './SearchForm'
import BrowseLearningCircles from './BrowseLearningCircles'
import LoadMoreResults from './LoadMoreResults'
import { LEARNING_CIRCLES_LIMIT } from '../../../constants'
import ApiHelper from '../../../helpers/ApiHelper'
import '../../stylesheets/search.scss'

export default class LearningCircles extends Component {

  constructor(props) {
    super(props);
    this.state = { searchResults: [] };
    this.api = new ApiHelper('learningCircles');
    this.searchByLocation = (q) => this._searchByLocation(q);
    this.populateLearningCircles = () => this._populateLearningCircles();
    this.showMoreResults = (q) => this._showMoreResults(q);
    this.searchCallback = (response, args) => this._searchCallback(response, args);
    this.populateLearningCircles();
  }

  _populateLearningCircles() {
    const params = {
      active: true,
      signup: 'open',
      limit: LEARNING_CIRCLES_LIMIT
    }

    const opts = { params, callback: this.searchCallback }

    this.api.fetchResource(opts);
  }

  _searchByLocation(query) {
    const params = {
      active: true,
      signup: 'open',
      limit: LEARNING_CIRCLES_LIMIT,
      city: query
    }

    const opts = { params, callback: this.searchCallback }

    this.api.fetchResource(opts);
  }

  _showMoreResults() {
    let params;

    if (this.state.currentQuery) {
      const optsCopy = Object.assign({}, this.state.currentQuery);
      params = Object.assign(optsCopy, { offset: this.state.searchResults.length });
    } else {
      params = {
        active: true,
        signup: 'open',
        limit: LEARNING_CIRCLES_LIMIT,
        offset: this.state.searchResults.length
      }
    }

    const opts = {
      params,
      callback: this.searchCallback,
      appendResults: true
    }

    this.api.fetchResource(opts);
  }

  _searchCallback(response, opts) {
    const results = opts.appendResults ? this.state.searchResults.concat(response.items) : response.items;
    this.setState({
      searchResults: results,
      currentQuery: opts.params,
      totalResults: response.count
    })
  }

  render() {
    return (
      <div className="search-and-results">
        <SearchForm
          searchByLocation={ this.searchByLocation }
        />
        <BrowseLearningCircles
          learningCircles={ this.state.searchResults }
        />
        <LoadMoreResults
          visibleSearchResults={ this.state.searchResults.length }
          totalSearchResults={ this.state.totalResults }
          showMoreResults={ this.showMoreResults }
        />
      </div>
    );
  }
}

