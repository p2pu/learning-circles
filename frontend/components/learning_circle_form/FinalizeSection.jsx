import React from 'react'
import TextareaWithLabel from '../form_fields/TextareaWithLabel'

const FinalizeSection = (props) => {
  const handleImageUpload = (pictures) => {
    props.updateFormData({ image: pictures })
  }

  return (
    <div>
      <TextareaWithLabel
        label={'What are your personal goals as you facilitate this learning circle?'}
        value={props.learningCircle.facilitator_goal || ''}
        handleChange={props.updateFormData}
        name={'facilitator_goal'}
        id={'id_facilitator_goal'}
        errorMessage={props.errors.facilitator_goal}
      />
      <TextareaWithLabel
        label={'What questions or concerns do you have about the learning circle? Is there anything that you want feedback on before you get started?'}
        value={props.learningCircle.facilitator_concerns || ''}
        handleChange={props.updateFormData}
        name={'facilitator_concerns'}
        id={'id_facilitator_concerns'}
        errorMessage={props.errors.facilitator_concerns}
      />
    </div>
  )
}

export default FinalizeSection;
