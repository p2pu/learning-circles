import React from 'react'
import InputWithLabel from '../common/InputWithLabel'
import PlaceSelect from './form_fields/PlaceSelect'

const LocationSection = (props) => {
  return (
    <div>
      <div className={`input-with-label form-group`} >
        <label htmlFor={props.city}>In which city is this happening?</label>
        <PlaceSelect
          name={'city'}
          id={'id_city'}
          label='Start typing any city name'
          placeObjectId={props.learningCircle.placeObjectId}
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
      />
      <InputWithLabel
        label={'What is the specific meeting spot?'}
        value={props.learningCircle.venue_details || ''}
        placeholder={'Eg. Room 409, fourth floor'}
        handleChange={props.updateFormData}
        name={'venue_details'}
        id={'id_venue_details'}
        errorMessage={props.errors.venue_details}
      />
      <InputWithLabel
        label={'What is the address of the venue?'}
        value={props.learningCircle.venue_address || ''}
        placeholder={'Write it out as if you were writing a letter'}
        handleChange={props.updateFormData}
        name={'venue_address'}
        id={'id_venue_address'}
        errorMessage={props.errors.venue_address}
      />
    </div>
  );
}

export default LocationSection;
