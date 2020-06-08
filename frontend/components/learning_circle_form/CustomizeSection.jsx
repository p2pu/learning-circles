import React from 'react'
import {TextareaWithLabel, InputWithLabel, ImageUploader} from 'p2pu-components'
import UrlInput from './UrlInput'


const CourseDescriptionInput = (props) => {
  const onChange = (e) => {
    props.handleChange({ [props.name]: e.currentTarget.value })
  }

  const insertCourseDescription = (e) => {
    e.preventDefault()
    if (!props.course.caption) {
      return props.showAlert('Please select a course.', 'warning')
    }

    props.handleChange({ [props.name]: props.course.caption })
  }

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>
        <div>{`Describe the course materials you'll be using. `}<a href="#" onClick={insertCourseDescription}>Copy in the course description.</a></div>
      </label>
      <textarea
        className='form-control'
        type={props.type || 'text'}
        name={props.name}
        id={props.id}
        onChange={onChange}
        value={props.value}
        placeholder={props.placeholder}
      />
      {
        props.errorMessage &&
        <div className='error-message minicaps'>
          { props.errorMessage }
        </div>
      }
    </div>
  )
}

const TitleInput = (props) => {
  const onChange = (e) => {
    props.handleChange({ [props.name]: e.currentTarget.value })
  }

  const insertCourseTitle = (e) => {
    e.preventDefault()
    if (!props.course.caption) {
      return props.showAlert('Please select a course.', 'warning')
    }

    props.handleChange({ [props.name]: props.course.title })
  }

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>
        <div>{`Set a custom title for your learning circle. `}<a href="#" onClick={insertCourseTitle}>Copy in the course title.</a></div>
      </label>
      <input
        className='form-control'
        type={props.type || 'text'}
        name={props.name}
        id={props.id}
        onChange={onChange}
        value={props.value || props.defaultValue}
        placeholder={props.placeholder}
        required={props.required || false}
        min={props.min}
        max={props.max}
        disabled={props.disabled}
      />
      {
        props.errorMessage &&
        <div className='error-message minicaps'>
          { props.errorMessage }
        </div>
      }
    </div>
  )
}

const CustomizeSection = (props) => {
  const handleImageUpload = ({image}) => {
    props.updateFormData({ image_url: image })
  }

  return (
    <div>
      <TitleInput
        value={props.learningCircle.name || ''}
        handleChange={props.updateFormData}
        name={'name'}
        id={'id_name'}
        errorMessage={props.errors.name}
        course={props.learningCircle.course}
        showAlert={props.showAlert}
      />
      <TextareaWithLabel
        label={'Share a welcome message with potential learners.'}
        value={props.learningCircle.description || ''}
        handleChange={props.updateFormData}
        name={'description'}
        id={'id_description'}
        errorMessage={props.errors.description}
        required={true}
      />
      <CourseDescriptionInput
        value={props.learningCircle.course_description || ''}
        handleChange={props.updateFormData}
        name={'course_description'}
        id={'id_course_description'}
        errorMessage={props.errors.course_description}
        course={props.learningCircle.course}
        showAlert={props.showAlert}
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
        handleChange={handleImageUpload}
        name={'image'}
        id={'id_image'}
        image={props.learningCircle.image_url}
        errorMessage={props.errors.image}
        imageUploadUrl='/api/upload_image/'

      />
    </div>
  )
}

export default CustomizeSection;
