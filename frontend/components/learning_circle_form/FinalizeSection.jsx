import React from 'react'
import { TextareaWithLabel, SelectWithLabel } from 'p2pu-components'

const FinalizeSection = (props) => {

  const populateTeamOptions = (team) => {
    return team.map(teamMember => {
      const parsedTeamMember = JSON.parse(teamMember)
      return {label: parsedTeamMember.firstName + ' ' + parsedTeamMember.lastName + ', ' + parsedTeamMember.email,
      value: parsedTeamMember.id}
    })
  }

  const handleFacilitatorSelect = (value) => {
    props.closeAlert()
    if(facilitatorsRemoved(value, props)) {
      const removedFacilitators = props.learningCircle.facilitators.filter(x => !value.facilitators.includes(x));
      if(removedFacilitators.includes(props.userId)) {
        props.showAlert('Removing yourself as a facilitator means you will no longer have access to this learning circle.', 'warning')
      }
    }
    props.updateFormData(value)
  }

  const facilitatorsRemoved = (value) => {
    return value.facilitators && props.learningCircle.facilitators && 
    props.learningCircle.facilitators.length > value.facilitators.length;
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
    <SelectWithLabel
      className='lc-co-facilitator-input'
      options={populateTeamOptions(props.team)}
      name={'facilitators'}
      id={'id_facilitators'}
      errorMessage={props.errors.facilitators}
      value={props.learningCircle.facilitators}
      handleChange={handleFacilitatorSelect}
      label="Select your co-facilitator(s)"
      isMulti={true}
    />
  </div>
  );
};

export default FinalizeSection;
