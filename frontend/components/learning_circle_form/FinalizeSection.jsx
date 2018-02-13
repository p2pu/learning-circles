import React from 'react'
import TextareaWithLabel from '../form_fields/TextareaWithLabel'
import InputWithLabel from '../form_fields/InputWithLabel'
import ImageUploader from '../form_fields/ImageUploader'

const FinalizeSection = (props) => {
  const handleImageUpload = (pictures) => {
    props.updateFormData({ image: pictures })
  }

  return (
    <div>
      <InputWithLabel
        label={'What is your personal goal in facilitating this learning circle?'}
        value={props.learningCircle.facilitator_goal || ''}
        handleChange={props.updateFormData}
        name={'facilitator_goal'}
        id={'id_facilitator_goal'}
        errorMessage={props.errors.facilitator_goal}
      />
      <InputWithLabel
        label={'What concerns do you have about the learning circle? Is there anything specific that you want feedback on before you get started?'}
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
