import React from 'react'

const InputWithLabel = ({ name, id, classes, label, handleChange, value, placeholder, type }) => {
  const onChange = (e) => {
    handleChange({ [name]: e.currentTarget.value })
  }

  return(
    <div className={`input-with-label form-group ${classes}`}>
      <label htmlFor={name}>{label}</label>
      <input
        className='form-control'
        type={type || 'text'}
        name={name}
        id={id}
        onChange={onChange}
        value={value || ''}
        placeholder={placeholder}
      />
    </div>
  )
}

export default InputWithLabel;