import React, { Component } from 'react'
import SearchAndFilter from './SearchAndFilter'
import ResultsDisplay from './ResultsDisplay'
import SearchTags from './SearchTags'
import { SEARCH_PROPS } from '../../../constants'
import ApiHelper from '../../../helpers/ApiHelper'
import { debounce } from 'lodash';


export default class Search extends Component {
  constructor(props) {
    super(props)
    this.state = {
      searchResults: [],
      distance: 50,
      useMiles: true,
    }
    this.handleChange = (s) => this._handleChange(s);
    this.handleInputChange = () => this._handleInputChange();
    this.handleSearchBarSubmit = (query) => this._handleSearchBarSubmit(query);
    this.searchCallback = (response, opts) => this._searchCallback(response, opts);
    this.updateQueryParams = (params) => this._updateQueryParams(params);
    this.sendQuery = () => this._sendQuery();
    this.fetchCourseCategories = () => this._fetchCourseCategories();
    this.loadInitialData = () => this._loadInitialData();
  }

  componentDidMount() {
    this.loadInitialData();
  }

  _loadInitialData() {
    this.updateQueryParams({ active: true, signup: 'open', order: 'title' });
  }

  _sendQuery() {
    const params = this.state;
    const opts = { params, callback: this.searchCallback };
    const api = new ApiHelper(this.props.searchSubject);

    api.fetchResource(opts);
  }

  _updateQueryParams(params) {
    this.setState(params, debounce(this.sendQuery), 300);
  }

  _handleChange(selected) {
    const query = selected ? selected.label : selected;
    this.props.searchByLocation(query);
    this.setState({ value: selected });
  }

  _handleInputChange() {
    this.props.clearResults();
  }

  _searchCallback(response, opts) {
    const results = opts.appendResults ? this.state.searchResults.concat(response.items) : response.items;

    this.setState({
      searchResults: results,
      currentQuery: opts.params,
      totalResults: response.count
    }, this.props.scrollToTop)
  }

  render() {
    const filterCollection = SEARCH_PROPS[this.props.searchSubject].filters;
    const placeholder = SEARCH_PROPS[this.props.searchSubject].placeholder;
    const resultsSubtitle = SEARCH_PROPS[this.props.searchSubject].resultsSubtitle;

    return(
      <div className="page">
        <SearchAndFilter
          placeholder={placeholder}
          updateQueryParams={this.updateQueryParams}
          filterCollection={filterCollection}
          searchSubject={this.props.searchSubject}
          {...this.state}
        />
        <ResultsDisplay
          resultsSubtitle={resultsSubtitle}
          updateQueryParams={this.updateQueryParams}
          {...this.state}
          {...this.props}
        />
      </div>
    )
  }
}
