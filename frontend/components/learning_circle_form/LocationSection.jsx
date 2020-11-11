import React from 'react'
import {
  PlaceSelect,
  InputWithLabel,
  SwitchWithLabels,
  LanguageSelect
} from 'p2pu-components'


const LocationSection = (props) => {
  const place = !!props.learningCircle.place_id ? { objectID: props.learningCircle.place_id } : props.learningCircle.place
  return (
    <div>
      <PlaceSelect
        label='What city are you meeting in?'
        helpText='If you’re meeting online, indicate where you’re based.'
        name='place'
        id='place_id'
        classes="form-group"
        value={place}
        handleChange={props.updateFormData}
        errorMessage={props.errors.city}
        required={true}
      />
      <SwitchWithLabels
        label='Are you meeting online?'
        trueLabel='Yes'
        falseLabel='No'
        handleChange={props.updateFormData}
        value={Boolean(props.learningCircle.online)}
        name='online'
      />
      <InputWithLabel
        label='Where will you meet?'
        placeholder={props.learningCircle.online?'Eg. Online':'Eg. Pretoria Library'}
        value={props.learningCircle.venue_name || ''}
        handleChange={props.updateFormData}
        name='venue_name'
        id='id_venue_name'
        errorMessage={props.errors.venue_name}
        required={true}
      />
      <InputWithLabel
        label='What is the specific meeting spot?'
        placeholder={props.learningCircle.online?'Eg. Using Jitsi':'Eg. Room 409, fourth floor'}
        value={props.learningCircle.venue_details || ''}
        handleChange={props.updateFormData}
        name='venue_details'
        id='id_venue_details'
        errorMessage={props.errors.venue_details}
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
