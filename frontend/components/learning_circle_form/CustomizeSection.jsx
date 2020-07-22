import React from 'react'
import { TextareaWithLabel, InputWithLabel, ImageUploader, URLInputWithLabel } from "p2pu-components";
import { DEFAULT_LC_IMAGE } from '../../helpers/constants'
import RichTextEditor from './RichTextEditor'


const CustomizeSection = (props) => {
  const insertCourseDescription = (e) => {
    e.preventDefault()
    if (!props.learningCircle.course.caption) {
      return props.showAlert('Please select a course.', 'warning')
    }

    console.log("props.learningCircle.course", props.learningCircle.course)

    props.updateFormData({ course_description: props.learningCircle.course.caption })
  }

  const insertCourseTitle = (e) => {
    e.preventDefault()
    if (!props.learningCircle.course.caption) {
      return props.showAlert('Please select a course.', 'warning')
    }

    props.updateFormData({ name: props.learningCircle.course.title })
  }

  return (
    <div>
      <InputWithLabel
        value={props.learningCircle.name || ''}
        handleChange={props.updateFormData}
        name={'name'}
        id={'id_name'}
        errorMessage={props.errors.name}
        label={<div>{`Set a custom title for your learning circle. `}<a href="#" onClick={insertCourseTitle}>Copy in the course title.</a></div>}
        maxLength={125}
        helpText={'Maximum 125 characters'}
      />
      <RichTextEditor
        label={'Share a welcome message with potential learners.'}
        value={props.learningCircle.description || ''}
        handleChange={props.updateFormData}
        name={'description'}
        id={'id_description'}
        errorMessage={props.errors.description}
        required={true}
        maxLength={1000}
        helpText={'Maximum 1,000 characters'}
      />
      <RichTextEditor
        value={props.learningCircle.course_description || ''}
        handleChange={props.updateFormData}
        name={'course_description'}
        id={'id_course_description'}
        errorMessage={props.errors.course_description}
        label={<div>{`Describe the course materials you'll be using. `}<a href="#" onClick={insertCourseDescription}>Copy in the course description.</a></div>}
        helpText={'Maximum 1,000 characters'}
        maxLength={1000}
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
      <URLInputWithLabel
        label={'Do you have a website you want to link to?'}
        value={props.learningCircle.venue_website || ''}
        placeholder={'E.g. https://www.pretorialibrary.com'}
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
        image={props.learningCircle.image_url || DEFAULT_LC_IMAGE}
        errorMessage={props.errors.image}
        imageUploadUrl='/api/upload_image/'
        helpText="If you don't upload your own image, we'll use the default one shown below."
      />
    </div>
  )
}

export default CustomizeSection;
