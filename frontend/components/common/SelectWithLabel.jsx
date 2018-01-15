import React from 'react'
import Select from 'react-select'

const SelectWithLabel = (props) => {
  return(
    <div className={`select-with-label ${props.classes}`} >
      <label htmlFor={props.name}>{props.label}</label>
      <Select
        name={ props.name }
        className={ props.selectClasses }
        value={ props.value }
        options={ props.options }
        onChange={ props.onChange }
        onInputChange={ props.onInputChange }
        noResultsText={ props.noResultsText }
        placeholder={ props.placeholder }
        multi={ props.multi || false }
      />
    </div>
  )
}

export default SelectWithLabel;