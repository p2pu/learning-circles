import React from 'react'
import axios from 'axios';
import InputWrapper from 'p2pu-components/dist/InputFields/InputWrapper'
import AsyncCreatableSelect from 'react-select/async-creatable';
import InputWithLabel from 'p2pu-components/dist/InputFields/InputWithLabel'


const CountryInput = props => {
  const { handleChange, name, value, disabled, selectClasses, ...rest } = props;

  const handleSelect = selected => {
    const {country, country_en} = selected.value;
    handleChange({ country, country_en });
  }

  const searchPlaces = (query) => {
    const url = "/api/places/search/country/";
    return axios({
      url,
      method: 'GET',
      params: { "query": query },
    }).then(res => {
      let options = res.data.countries.map(country => (
        {label: country['country'], value: country}
      ));
      return options
    }).catch(err => {
      console.log(err)
    })
  }

  const handleCreateOption = label => {
    const newOption = {
      label,
      value: { country: label, country_en: label }
    }
    handleSelect(newOption);
  }

  return (
    <InputWrapper
      {...props}
    >
      <AsyncCreatableSelect
        name={ name }
        cacheOptions
        className={ `react-select ${selectClasses}` }
        value={ !!value.country?{label: value.country, value}:null }
        onChange={ handleSelect }
        onCreateOption={ handleCreateOption }
        loadOptions={ searchPlaces }
        isDisabled={ disabled }
        classNamePrefix={'place-select'}
        defaultOptions
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
  );
}


const PlaceInput = (props) => {
  const {city, country, country_en, region} = props.value;
  const handleChange = update => {
    props.handleChange({...props.value, ...update, place_id: null, latitude: null, longitude: null });
  };
  return (
    <div>
      <label>{props.label}</label>
      <CountryInput
        label='Country'
        placeholder="Start typing a country name..."
        name="country"
        handleChange={handleChange}
        value={ {country, country_en} }
      />
      <InputWithLabel
        label="Region"
        placeholder="Enter the region or province."
        name="region"
        handleChange={handleChange}
        errorMessage={props.errors.region}
        value={region}
      />
      <InputWithLabel
        label="City"
        placeholder="Enter the City"
        name="city"
        handleChange={handleChange}
        errorMessage={props.errors.city}
        value={city}
      />
    </div>
  );
}

export default PlaceInput
