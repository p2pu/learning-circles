import React, { useState } from 'react'
import { TextareaWithLabel, SelectWithLabel } from 'p2pu-components'

const FinalizeSection = (props) => {

  const [showSelfRemovalWarning, setShowSelfRemovalWarning] = useState(false);

  const populateTeamOptions = (team) => {
    return team.map(teamMember => {
      const parsedTeamMember = JSON.parse(teamMember)
      return {label: parsedTeamMember.firstName + ' ' + parsedTeamMember.lastName + ', ' + parsedTeamMember.email,
      value: parsedTeamMember.id}
    })
  }

  const handleFacilitatorSelect = (value) => {
      const removedFacilitators = props.learningCircle.facilitators.filter(x => value.facilitators === null || !value.facilitators.includes(x));
      if(removedFacilitators.includes(props.userId)) {
        setShowSelfRemovalWarning(true);
      }
    props.updateFormData(value)
  }

  const addCurrentUserToFacilitators = () => {
    if(props.learningCircle.facilitators) {
      props.learningCircle.facilitators.push(props.userId);
    }
    else {
      props.learningCircle.facilitators = [props.userId];
    }
    setShowSelfRemovalWarning(false);
  }

  return (
  <div>
    <TextareaWithLabel
      label={'What do you hope to achieve by facilitating this learning circle?'}
      value={props.learningCircle.facilitator_goal || ''}
      handleChange={props.updateFormData}
      name={'facilitator_goal'}
      id={'id_facilitator_goal'}
      errorMessage={props.errors.facilitator_goal}
    />
    <TextareaWithLabel
      label={'Is there anything that we can help you with as you get started?'}
      value={props.learningCircle.facilitator_concerns || ''}
      handleChange={props.updateFormData}
      name={'facilitator_concerns'}
      id={'id_facilitator_concerns'}
      errorMessage={props.errors.facilitator_concerns}
    />
    <div className='lc-co-facilitator-input'>
      <SelectWithLabel
        options={populateTeamOptions(props.team)}
        name={'facilitators'}
        id={'id_facilitators'}
        errorMessage={props.errors.facilitators}
        value={props.learningCircle.facilitators}
        handleChange={handleFacilitatorSelect}
        label="Select your co-facilitator(s)"
        isMulti={true}
      />
      {(showSelfRemovalWarning) &&
      <div className="alert alert-warning rm-facilitator-warning" role="warning">
        <p>You are removing yourself as a facilitator and will therefore no longer have access to this learning circle.</p>
        <hr/>
        <button type="button" className="btn btn-warning btn-sm" onClick={addCurrentUserToFacilitators}>Don't remove me</button>
      </div>
      }
    </div>
  </div>
  );
};

export default FinalizeSection;
