import React from 'react'
import TextareaWithLabel from '../form_fields/TextareaWithLabel'
import InputWithLabel from '../form_fields/InputWithLabel'
import ImageUploader from '../form_fields/ImageUploader'

const CustomizeSection = (props) => {
  const handleImageUpload = (pictures) => {
    props.updateFormData({ image: pictures })
  }

  return (
    <div>
      <TextareaWithLabel
        label={'Share a welcome message with potential learners.'}
        value={props.learningCircle.description || ''}
        handleChange={props.updateFormData}
        name={'description'}
        id={'id_description'}
        errorMessage={props.errors.description}
        required={true}
      />
      <InputWithLabel
        label={'Is there another question that you want people to answer when they sign up for your learning circle? If so, write that here:'}
        value={props.learningCircle.signup_question || ''}
        handleChange={props.updateFormData}
        placeholder={'How did you hear about this learning circle?'}
        name={'signup_question'}
        id={'id_signup_question'}
        errorMessage={props.errors.signup_question}
      />
      <InputWithLabel
        label={'Do you have a website you want to link to?'}
        value={props.learningCircle.venue_website || ''}
        placeholder={'E.g. www.pretorialibrary.com'}
        handleChange={props.updateFormData}
        name={'venue_website'}
        id={'id_venue_website'}
        errorMessage={props.errors.venue_website}
      />
      <ImageUploader
        label={'Care to add an image?'}
        handleChange={props.updateFormData}
        name={'image'}
        id={'id_image'}
        image={props.learningCircle.image}
        errorMessage={props.errors.image}
      />
    </div>
  )
}

export default CustomizeSection;
