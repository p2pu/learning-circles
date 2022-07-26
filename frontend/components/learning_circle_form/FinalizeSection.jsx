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
      handleChange={props.updateFormData}
      label="Select your co-facilitator(s)"
      isMulti={true}
    />
  </div>
  );
};

export default FinalizeSection;
