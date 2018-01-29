import React from 'react'

const CheckboxWithLabel = ({ name, id, classes, label, handleChange, checked }) => {
  const onChange = (e) => {
    handleChange({ [name]: e.currentTarget.checked })
  }

  return(
    <div className={`checkbox-with-label label-right ${classes}`} >
      <input
        type="checkbox"
        name={name}
        id={id || name}
        onChange={onChange}
        checked={checked}
        style={{marginRight: '10px'}}
      />
      <label htmlFor={name}>{label}</label>
    </div>
  )
}

export default CheckboxWithLabel;