import React from 'react'
import { TextareaWithLabel, SelectWithLabel } from 'p2pu-components'

const FinalizeSection = (props) => {

  const populateTeamOptions = (team) => {
    console.log(props.learningCircle)
    return team.map(teamMember => {
      return {label: teamMember.firstName + ' ' + teamMember.lastName + ', ' + teamMember.email,
      value: teamMember.id}
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
      name={'co_facilitators'}
      id={'id_co_facilitators'}
      value={props.learningCircle.co_facilitators}
      handleChange={props.updateFormData}
      label="Select your co-facilitator(s)"
      isMulti={true}
    />
  </div>
  );
};

export default FinalizeSection;
