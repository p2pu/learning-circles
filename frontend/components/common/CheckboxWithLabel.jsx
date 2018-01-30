import React from 'react'

const CheckboxWithLabel = (props) => {
  const onChange = (e) => {
    handleChange({ [props.name]: e.currentTarget.checked })
  }

  return(
    <div className={`checkbox-with-label label-right ${props.classes}`} >
      <input
        type="checkbox"
        name={props.name}
        id={props.id || props.name}
        onChange={props.onChange}
        checked={props.checked}
        style={{marginRight: '10px'}}
      />
      <label htmlFor={props.name}>{props.label}</label>
      {
        props.errorMessage &&
        <div className='error-message minicaps'>
          { props.errorMessage }
        </div>
      }
    </div>
  )
}

export default CheckboxWithLabel;