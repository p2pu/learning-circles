import React from 'react'

const InputWithLabel = (props) => {
  const onChange = (e) => {
    props.handleChange({ [props.name]: e.currentTarget.value })
  }

  return(
    <div className={`input-with-label form-group ${props.classes}`}>
      <label htmlFor={props.name}>{props.label}</label>
      <input
        className='form-control'
        type={props.type || 'text'}
        name={props.name}
        id={props.id}
        onChange={onChange}
        value={props.value || ''}
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

export default InputWithLabel;