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
        value={props.learningCircle.personal_goal || ''}
        handleChange={props.updateFormData}
        name={'personal_goal'}
        id={'id_personal_goal'}
        errorMessage={props.errors.personal_goal}
      />
      <InputWithLabel
        label={'What concerns do you have about the learning circle? Is there anything specific that you want feedback on before you get started?'}
        value={props.learningCircle.concerns || ''}
        handleChange={props.updateFormData}
        name={'concerns'}
        id={'id_concerns'}
        errorMessage={props.errors.concerns}
      />
    </div>
  )
}

export default FinalizeSection;
