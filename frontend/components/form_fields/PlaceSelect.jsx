import React, { Component } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { compact, uniqBy, sortBy } from 'lodash';
import { EXTERNAL_APIS, KANSAS_CITY_OPTION } from '../../constants';

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
    if (!!this.props.place_id) {
      this.fetchPlaceById();
    } else if (this.props.city === 'Kansas City') {
      const value = KANSAS_CITY_OPTION;
      this.setState({ value });
    } else if (this.props.city) {
      const value = { label: this.props.city, value: this.props.city }
      this.setState({ value });
    }
  }

  _handleChange(selected) {
    let cityData = {};

    if (selected) {
      cityData = {
        city: selected.value.locale_names ? selected.value.locale_names.default[0] : selected.value,
        latitude: selected.value._geoloc ? selected.value._geoloc.lat : null,
        longitude: selected.value._geoloc ? selected.value._geoloc.lng : null,
        place_id: selected.value.objectID ? selected.value.objectID : null,
      }
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

    return axios({
      data,
      url,
      method
    }).then(res => {
      let options = res.data.hits.map(place => this.generateCityOption(place));
      // Kansas City, MO is missing from the Algolia places API
      // so we're manually adding it in
      // TODO: don't do this
      if (query.toLowerCase().includes('kansas')) {
        options.unshift(KANSAS_CITY_OPTION)
      }
      return { options }
    }).catch(err => {
      console.log(err)
    })
  }

  _fetchPlaceById() {
    const url = `${EXTERNAL_APIS.algolia}/${this.props.place_id}`;

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
      label: `${place.locale_names.default[0]}, ${place.administrative[0]}, ${place.country.default}`,
      value: place
    }
  }

  render() {
    const options = this.state.hits.map((place) => {
      return this.generateCityOption(place)
    })

    return(
      <div>
        <Select.AsyncCreatable
          name={ this.props.name }
          className={ `city-select ${this.props.classes}` }
          value={ this.state.value }
          options={ options }
          onChange={ this.handleChange }
          noResultsText='No results for this city'
          placeholder='Start typing a city name...'
          loadOptions={this.searchPlaces}
        />
        {
          this.props.errorMessage &&
          <div className="error-message minicaps">{this.props.errorMessage}</div>
        }
      </div>
    )
  }
}
