import React, { useState } from 'react'
import { TextareaWithLabel, SelectWithLabel, InputWithLabel, SwitchWithLabels } from 'p2pu-components'

const SignupLimit = (props) => {
  // maxSignups indicates if there is a hard limit set, iow 
  // you can toggle unlimited signups if it isn't null
  let maxSignups = null
  let defaultLimit = 20
  if (window.maxSignups !== undefined){
    maxSignups = window.maxSignups
    defaultLimit = maxSignups
  }

  const handleSwitch = ({enableLimit}) => {
    if (enableLimit) {
      props.updateFormData({'signup_limit': defaultLimit})
    } else {
      props.updateFormData({'signup_limit': undefined})
    }
  }

  return (
    <>
      { (maxSignups === null) && 
        <SwitchWithLabels
          label={'Do you want to limit the number of signups?'}
          trueLabel='Yes'
          falseLabel='No'
          handleChange={handleSwitch}
          name='enableLimit'
          value={props.learningCircle.signup_limit !== undefined}
        />
      }
      { (props.learningCircle.signup_limit !== undefined || maxSignups !== null) &&
        <InputWithLabel
          label={'What is the maximum number of signups?'}
          type='number'
          value={props.learningCircle.signup_limit || defaultLimit}
          handleChange={props.updateFormData}
          name='signup_limit'
          id='id_signup_limit'
          errorMessage={props.errors.signup_limit}
          min={0}
          max={maxSignups}
        />
      }
      <div>
        <a href="https://docs.p2pu.org/tools-and-resources/tools-for-learning-circles/managing-learning-circles#limiting-learning-circle-signups">More info about signup limits</a>
      </div>
    </>
  )
}

const FinalizeSection = (props) => {

  const [showSelfRemovalWarning, setShowSelfRemovalWarning] = useState(false);

  const populateTeamOptions = (team) => {
    return team.map(teamMember => {
      return {label: teamMember.firstName + ' ' + teamMember.lastName + ', ' + teamMember.email,
      value: teamMember.id}
    })
  }

  const handleFacilitatorSelect = (value) => {
    if(props.learningCircle.facilitators) {
      const removedFacilitators = props.learningCircle.facilitators.filter(x => value.facilitators === null || !value.facilitators.includes(x));
      if(removedFacilitators.includes(props.userId)) {
        setShowSelfRemovalWarning(true);
      }
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

  const hasTeam = () => {
    return props.team.length > 0;
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
    <SignupLimit
      {...props}
    />
    <div className='lc-co-facilitator-input'>
      <SelectWithLabel
        options={populateTeamOptions(props.team)}
        name={'facilitators'}
        id={'id_facilitators'}
        disabled={!hasTeam()}
        errorMessage={props.errors.facilitators}
        value={props.learningCircle.facilitators}
        handleChange={handleFacilitatorSelect}
        label="Select your co-facilitator(s)"
        isMulti={true}
      />
      {(!hasTeam()) && <small>This feature is only available to teams</small>}
      {(showSelfRemovalWarning) &&
      <div className="alert alert-warning rm-facilitator-warning" role="warning">
        <p>You are removing yourself as a facilitator and will therefore no longer have access to this learning circle.</p>
        <button type="button" className="p2pu-btn dark" onClick={addCurrentUserToFacilitators}>Don't remove me</button>
      </div>
      }
    </div>
  </div>
  );
};

export default FinalizeSection;
