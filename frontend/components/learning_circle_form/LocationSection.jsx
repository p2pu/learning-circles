import React from 'react'
import {
  PlaceSelect,
  InputWithLabel,
  LanguageSelect
} from 'p2pu-components'


const LocationSection = (props) => {
  return (
    <div>
      <PlaceSelect
        label={'Start typing any city name'}
        name={'place'}
        classes="form-group"
        value={props.learningCircle.place}
        handleChange={props.updateFormData}
        errorMessage={props.errors.place}
      />
      <InputWithLabel
        label={'Where will you meet?'}
        value={props.learningCircle.venue_name || ''}
        placeholder={'Eg. Pretoria Library'}
        handleChange={props.updateFormData}
        name={'venue_name'}
        errorMessage={props.errors.venue_name}
        required={true}
      />
      <InputWithLabel
        label={'What is the specific meeting spot?'}
        value={props.learningCircle.venue_details || ''}
        placeholder={'Eg. Room 409, fourth floor'}
        handleChange={props.updateFormData}
        name={'venue_details'}
        errorMessage={props.errors.venue_details}
        required={true}
      />
      <InputWithLabel
        label={'What is the address of the venue?'}
        value={props.learningCircle.venue_address || ''}
        placeholder={'Write it out as if you were writing a letter'}
        handleChange={props.updateFormData}
        name={'venue_address'}
        errorMessage={props.errors.venue_address}
        required={true}
      />
      <LanguageSelect
        label={'What is the primary language for this learning circle?'}
        value={props.learningCircle.language}
        handleChange={props.updateFormData}
        placeholder={'Pick a language'}
        name={'language'}
        errorMessage={props.errors.language}
        helpText={'Participants will receive communications in this language.'}
        isMulti={false}
      />
    </div>
  );
}

export default LocationSection;
