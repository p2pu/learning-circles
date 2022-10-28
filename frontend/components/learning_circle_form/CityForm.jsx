import React from 'react'
import axios from 'axios';
import InputWrapper from 'p2pu-components/dist/InputFields/InputWrapper'
import AsyncCreatableSelect from 'react-select/async-creatable';

const PLACE_ENDPOINT = '/api/cities';

const CountryInput = props => {

  const { label, name, id, value, required, disabled, errorMessage, helpText, classes, selectClasses, noResultsText, placeholder, isClearable, isMulti, ...rest } = props
  const { selected } = {};

  const handleSelect = selected => {
  }

  const searchPlaces = (query) => {
    const url = `${PLACE_ENDPOINT}/search/country/`;
    return axios({
      url,
      method: 'GET',
      params: { "query": query },
    }).then(res => {
      let options = res.data.countries.map(country => (
        {label: country['country'], value: country['country']}
      ));
      return options
    }).catch(err => {
      console.log(err)
    })
  }

  return (
    <InputWrapper
      label='Country'
      {...props}
    >
      <AsyncCreatableSelect
        name={ name }
        cacheOptions
        className={ `city-select ${selectClasses}` }
        value={ selected }
        onChange={ handleSelect }
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
  return (
    <InputWrapper
      label='Region'
      {...props}
    >
      <input type="text"  className="form-control"/>
    </InputWrapper>
  );
}

const CityInput = props => {
  return (
    <InputWrapper 
      label="City"
      {...props}
    >
      <input type="text"  className="form-control"/>
    </InputWrapper>
  );
}

const CityForm = (props) => {
  return (
    <form>
      <div>
        <label>What city are you meeting in?*</label>
        <CountryInput
          name="country"
        />
        <RegionInput
          name="region"
        />
        <CityInput
          name="city"
        />
      </div>
    </form>
  );
}

export default CityForm;
