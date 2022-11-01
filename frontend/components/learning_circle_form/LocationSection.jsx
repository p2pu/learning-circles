import React, {useState} from 'react'
import {
  InputWithLabel,
  SwitchWithLabels,
  LanguageSelect
} from 'p2pu-components'

import PlaceSelect from './place-select';
import CityForm from './CityForm';

const LocationSection = (props) => {
  const place = {
    city: props.learningCircle.city,
    region: props.learningCircle.region,
    country: props.learningCircle.country,
    country_en: props.learningCircle.country_en,
    latitude: props.learningCircle.latitude,
    longitude: props.learningCircle.longitude,
    place_id: props.learningCircle.place_id, // TODO geonameid
  };

  const addCity = props.learningCircle.addCity;
  const setAddCity = value => props.updateFormData({addCity: value});

  const onOnlineChanged = ({online}) => {
    let {venue_name} = props.learningCircle;
    if (online && !venue_name) {
      venue_name = 'Online'
    }
    props.updateFormData({online, venue_name});
  }
  return (
    <div>
      <SwitchWithLabels
        label='Are you meeting online?'
        trueLabel='Yes'
        falseLabel='No'
        handleChange={onOnlineChanged}
        value={Boolean(props.learningCircle.online)}
        name='online'
      />
      { !addCity && 
        <>
          <PlaceSelect
            label={props.learningCircle.online?'Where are you based?':'What city are you meeting in?'}
            name='place'
            id='place_id'
            classes="form-group"
            value={place}
            handleChange={props.updateFormData}
            errorMessage={props.errors.city}
            required={true}
          />
          <div claddName="form-text help-text">Click here if you don't see your city in the list <button className="p2pu-btn btn btn-sm blue" onClick={() => setAddCity(true)}>Add City</button></div>
        </>
      }
      { 
        addCity &&
        <>
          <CityForm 
            label={props.learningCircle.online?'Where are you based?':'What city are you meeting in?'}
            name='place'
            id='place_id'
            classes="form-group"
            value={place}
            handleChange={props.updateFormData}
            errorMessage={props.errors.city}
            required={true}
          /> 
          <div claddName="form-text help-text">Go back to search for your city in the list <button className="p2pu-btn btn btn-sm blue" onClick={() => setAddCity(false)}>Select City</button></div>
        </>
      }
      <InputWithLabel
        label='Where will you meet?'
        placeholder={props.learningCircle.online?'E.g. Online':'E.g. Pretoria Library'}
        value={props.learningCircle.venue_name || ''}
        handleChange={props.updateFormData}
        name='venue_name'
        id='id_venue_name'
        errorMessage={props.errors.venue_name}
        required={true}
      />
      <InputWithLabel
        label='What is the specific meeting spot?'
        placeholder={props.learningCircle.online?'E.g. Jit.si, Hangout, Zoom':'E.g. Room 409, fourth floor'}
        value={props.learningCircle.venue_details || ''}
        handleChange={props.updateFormData}
        name='venue_details'
        id='id_venue_details'
        errorMessage={props.errors.venue_details}
        required={true}
      />
      <InputWithLabel
        label='What is the meeting address?'
        helpText='This will be emailed to participants when they sign up.'
        placeholder='Write either the street address or meeting URL'
        value={props.learningCircle.venue_address || ''}
        handleChange={props.updateFormData}
        name='venue_address'
        id='id_venue_address'
        errorMessage={props.errors.venue_address}
        required={true}
      />
      <LanguageSelect
        label='What language should P2PU use to communicate details about your learning circle?'
        helpText='Participants will receive communications in this language.'
        placeholder='Pick a language'
        value={props.learningCircle.language}
        handleChange={props.updateFormData}
        name='language'
        id='id_language'
        errorMessage={props.errors.language}
        isMulti={false}
      />
    </div>
  );
}

export default LocationSection;
