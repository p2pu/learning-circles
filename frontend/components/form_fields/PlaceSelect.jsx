import React, { Component } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { compact, uniqBy, sortBy } from 'lodash';
import { EXTERNAL_APIS } from '../../constants';

import css from 'react-select/dist/react-select.css';


export default class PlaceSelect extends Component {
  constructor(props) {
    super(props);
    this.state = { hits: [], value: null };
    this.handleChange = (s) => this._handleChange(s);
    this.searchPlaces = (query) => this._searchPlaces(query);
    this.fetchPlaceById = () => this._fetchPlaceById();
    this.generateCityOption = (place) => this._generateCityOption(place);
  }

  componentWillMount() {
    if (!!this.props.placeObjectId) {
      this.fetchPlaceById();
    }
  }

  _handleChange(selected) {
    const cityData = {
      city: selected.value.locale_names.default[0],
      latitude: selected.value._geoloc.lat,
      longitude: selected.value._geoloc.lng,
      placeObjectId: selected.value.objectID,
    }

    this.props.handleSelect(cityData)
    this.setState({ value: selected })
  }

  _searchPlaces(query) {
    const url = `${EXTERNAL_APIS.algolia}/query/`;
    const data = {
      'type': 'city',
      'hitsPerPage': '10',
      'query': query
    };
    const method = 'post';
    axios({
      data,
      url,
      method
    }).then(res => {
      this.setState({ hits: res.data.hits })
    }).catch(err => {
      console.log(err)
    })
  }

  _fetchPlaceById() {
    const url = `${EXTERNAL_APIS.algolia}/${this.props.placeObjectId}`;

    axios.get(url)
      .then(res => {
        const value = this.generateCityOption(res.data)
        this.setState({ value })
      })
      .catch(err => {
        console.log(err)
      })
  }

  _generateCityOption(place) {
    return {
      label: `${place.locale_names.default}, ${place.administrative[0]}, ${place.country.default}`,
      value: place
    }
  }

  render() {
    const options = this.state.hits.map((place) => {
      return this.generateCityOption(place)
    })

    return(
      <div>
        <Select
          name={ this.props.name }
          className={ `city-select ${this.props.classes}` }
          value={ this.state.value }
          options={ options }
          onChange={ this.handleChange }
          onInputChange={ this.searchPlaces }
          noResultsText='No results for this city'
          placeholder='Start typing a city name...'
        />
        {
          this.props.errorMessage &&
          <div className="error-message minicaps">{this.props.errorMessage}</div>
        }
      </div>
    )
  }
}
