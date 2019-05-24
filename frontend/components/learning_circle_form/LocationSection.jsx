import React from 'react'
import PlaceSelect from 'p2pu-input-fields/dist/PlaceSelect'
import InputWithLabel from 'p2pu-input-fields/dist/InputWithLabel'
import LanguageSelect from 'p2pu-input-fields/dist/LanguageSelect'


const LocationSection = (props) => {
  return (
    <div>
      <div className={`input-with-label form-group`} >
        <label htmlFor={props.city}>In which city is this happening? *</label>
        <PlaceSelect
          name={'city'}
          id={'id_city'}
          label='Start typing any city name'
          place_id={props.learningCircle.place_id}
          city={props.learningCircle.city}
          region={props.learningCircle.region}
          country={props.learningCircle.country}
          country_en={props.learningCircle.country_en}
          handleSelect={props.updateFormData}
          errorMessage={props.errors.city}
        />
      </div>
      <InputWithLabel
        label={'Where will you meet?'}
        value={props.learningCircle.venue_name || ''}
        placeholder={'Eg. Pretoria Library'}
        handleChange={props.updateFormData}
        name={'venue_name'}
        id={'id_venue_name'}
        errorMessage={props.errors.venue_name}
        required={true}
      />
      <InputWithLabel
        label={'What is the specific meeting spot?'}
        value={props.learningCircle.venue_details || ''}
        placeholder={'Eg. Room 409, fourth floor'}
        handleChange={props.updateFormData}
        name={'venue_details'}
        id={'id_venue_details'}
        errorMessage={props.errors.venue_details}
        required={true}
      />
      <InputWithLabel
        label={'What is the address of the venue?'}
        value={props.learningCircle.venue_address || ''}
        placeholder={'Write it out as if you were writing a letter'}
        handleChange={props.updateFormData}
        name={'venue_address'}
        id={'id_venue_address'}
        errorMessage={props.errors.venue_address}
        required={true}
      />
      <LanguageSelect
        label={'What is the primary language for this learning circle?'}
        value={props.learningCircle.language}
        handleChange={props.updateFormData}
        placeholder={'Pick a language'}
        name={'language'}
        id={'id_language'}
        errorMessage={props.errors.language}
        helpText={'Participants will receive communications in this language.'}
      />
    </div>
  );
}

export default LocationSection;
