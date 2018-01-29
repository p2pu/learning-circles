import React, { Component } from 'react'
import axios from 'axios';

import { compact, uniqBy, sortBy } from 'lodash';
import Select from 'react-select';
import css from 'react-select/dist/react-select.css';


export default class PlaceSelect extends Component {
  constructor(props) {
    super(props);
    this.state = { hits: [] };
    this.handleChange = (s) => this._handleChange(s);
    this.searchPlaces = (query) => this._searchPlaces(query);
  }

  _handleChange(selected) {
    const cityData = {
      city: selected.value.locale_names.default,
      latitude: selected.value._geoloc.lat,
      longitude: selected.value._geoloc.lng
    }

    this.props.handleSelect(cityData)
    this.setState({ value: selected })
  }

  _searchPlaces(query) {
    const url = 'https://places-dsn.algolia.net/1/places/query/';
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

  render() {
    const options = this.state.hits.map((place, index) => {
      return {
        label: `${place.locale_names.default}, ${place.administrative[0]}, ${place.country.default}`,
        value: place
      }
    })

    return(
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
    )
  }
}
