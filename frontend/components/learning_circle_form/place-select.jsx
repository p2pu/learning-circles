import React, { Component } from 'react';
import axios from 'axios';
import AsyncSelect from 'react-select/async';
import AsyncCreatableSelect from 'react-select/async-creatable';
import InputWrapper from 'p2pu-components/dist/InputFields/InputWrapper'

const PLACE_ENDPOINT = '/api/cities';

export default class PlaceSelect extends Component {
  constructor(props) {
    super(props);
    let selected = null;
    if (props.value && props.value.city) {
      const {city, region, country} = props.value;
      selected = {
        label: `${city}${region?', '+region:''}${country?', '+country:''}`,
        value: props.value
      }
    }
    this.state = { hits: [], selected };
  }

  componentDidMount() {
    if (this.props.value) {
      const { value, name, handleChange } =  this.props

      if (!!value.objectID) {
        this.fetchPlaceById(value.objectID);
      }
    }
  }

  handleSelect = (selected) => {
    const value = selected ? selected.value : null
    this.props.handleChange({ ...value });
    this.setState({ selected });
  }

  searchPlaces = (query) => {
    const url = `${PLACE_ENDPOINT}/search/`;
    return axios({
      url,
      method: 'GET',
      params: { "query": query },
    }).then(res => {
      let options = res.data.cities.map(place => this.generateCityOption(place));
      return options
    }).catch(err => {
      console.log(err);
    })
  }

  fetchPlaceById = (placeId) => {
    const url = `${PLACE_ENDPOINT}/${placeId}/`;

    axios.get(url)
      .then(res => {
        const value = this.generateCityOption(res.data)
        this.handleSelect(value)
      })
      .catch(err => {
        console.log(err)
      })
  }

  generateCityOption = (place) => {
    return {
      label: `${place.city}, ${place.region}, ${place.country}`,
      value: place
    }
  }

  render() {
    const { label, name, id, value, required, disabled, errorMessage, helpText, classes, selectClasses, noResultsText, placeholder, isClearable, isMulti, ...rest } = this.props
    const { selected } = this.state;

    return(
      <InputWrapper
        label={label}
        name={name}
        id={id}
        required={required}
        disabled={disabled}
        errorMessage={errorMessage}
        helpText={helpText}
        classes={classes}
      >
        <AsyncSelect
          name={ name }
          cacheOptions
          className={ `city-select ${selectClasses}` }
          value={ selected }
          onChange={ this.handleSelect }
          noResultsText={ noResultsText }
          placeholder={ placeholder }
          loadOptions={ this.searchPlaces }
          isClearable={ isClearable }
          isMulti={ isMulti }
          isDisabled={ disabled }
          classNamePrefix={'place-select'}
          theme={theme => ({
            ...theme,
            colors: {
              ...theme.colors,
              primary: '#05c6b4',
              primary75: '#D3D8E6',
              primary50: '#e0f7f5',
              primary25: '#F3F4F8'
            },
          })}
          {...rest}
        />
      </InputWrapper>
    )
  }
}

PlaceSelect.defaultProps = {
  noResultsText: "No results for this city",
  placeholder: "Start typing a city name...",
  classes: "",
  selectClasses: "",
  name: "select-place",
  handleChange: (selected) => console.log("Implement a function to save selection", selected),
  isClearable: true,
  isMulti: false,
}

