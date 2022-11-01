import React from 'react'
import axios from 'axios';
import InputWrapper from 'p2pu-components/dist/InputFields/InputWrapper'
import AsyncCreatableSelect from 'react-select/async-creatable';


const CountryInput = props => {

  const { onChange, label, name, id, value, required, disabled, errorMessage, helpText, classes, selectClasses, noResultsText, placeholder, isClearable, isMulti, place, ...rest } = props

  const handleSelect = selected => {
    console.log(selected);
    const {country, country_en} = selected.value;
    onChange({ country, country_en });
  }

  const searchPlaces = (query) => {
    const url = "/api/cities/search/country/";
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
      label='Country'
      {...props}
    >
      <AsyncCreatableSelect
        name={ name }
        cacheOptions
        className={ `react-select ${selectClasses}` }
        value={ {label: value.country, value} }
        onChange={ handleSelect }
        onCreateOption={ handleCreateOption }
        noResultsText={ noResultsText }
        placeholder={ placeholder }
        loadOptions={ searchPlaces }
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
  );
}

const RegionInput = props => {
  // TODO should I just use input with label?
  const {name, value, onChange} = props;
  return (
    <InputWrapper
      label='Region'
      {...props}
    >
      <input 
        type="text"
        value={value}
        className="form-control"
        onChange={(e) => onChange({[name]: e.target.value})}
      />
    </InputWrapper>
  );
}

const CityInput = props => {
  const {name, value, onChange} = props;
  return (
    <InputWrapper 
      label="City"
      {...props}
    >
      <input 
        type="text"
        value={value}
        className="form-control"
        onChange={(e) => onChange({[name]: e.target.value})}
      />
    </InputWrapper>
  );
}

const CityForm = (props) => {
  const {city, country, country_en, region} = props.value;
  const handleChange = update => {
    console.log('change of scenery', update);
    props.handleChange({...props.value, ...update, place_id: null, latitude: null, longitude: null });
  };
  return (
    <div>
      <label>What city are you meeting in?*</label>
      <CountryInput
        name="country"
        onChange={handleChange}
        value={ {country, country_en} }
      />
      <RegionInput
        name="region"
        onChange={handleChange}
        value={region}
      />
      <CityInput
        name="city"
        onChange={handleChange}
        value={city}
      />
    </div>
  );
}

export default CityForm;
