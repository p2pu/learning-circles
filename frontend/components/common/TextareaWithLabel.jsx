import React from 'react'

const TextareaWithLabel = (props) => {
  const onChange = (e) => {
    handleChange({ [props.name]: e.currentTarget.value })
  }

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>{props.label}</label>
      <textarea
        className='form-control'
        type={props.type || 'text'}
        name={props.name}
        id={props.id}
        onChange={props.onChange}
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

export default TextareaWithLabel;