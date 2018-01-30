import React from 'react'
import TextareaWithLabel from '../common/TextareaWithLabel'
import InputWithLabel from '../common/InputWithLabel'
import ImageUploader from '../common/ImageUploader'

const FinalizeSection = (props) => {
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

export default FinalizeSection;
