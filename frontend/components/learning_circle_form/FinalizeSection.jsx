import React from 'react'
import TextareaWithLabel from 'p2pu-input-fields/dist/TextareaWithLabel'

const FinalizeSection = (props) => {
  const handleImageUpload = (pictures) => {
    props.updateFormData({ image: pictures })
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
    </div>
  )
}

export default FinalizeSection;
