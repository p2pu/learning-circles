import React from 'react'
import {TextareaWithLabel, InputWithLabel, ImageUploader} from 'p2pu-components'
import UrlInput from './UrlInput'

const CustomizeSection = (props) => {
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
      <UrlInput
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
        name={'image_url'}
        id={'id_image'}
        image={props.learningCircle.image_url}
        errorMessage={props.errors.image}
        imageUploadUrl='/api/upload_image/'
      />
    </div>
  )
}

export default CustomizeSection;
