import React from 'react'
import Slider from 'react-rangeslider'
import css from 'react-rangeslider/lib/index.css'

const RangeSliderWithLabel = (props) => {
  const disabledClass = props.disabled ? 'disabled' : '';
  const onChangeFunction = props.disabled ? null : props.handleChange;

  return (
    <div className={`range-slider-with-label label-left ${props.classes} ${disabledClass}`} >
      <label htmlFor={props.name}>{props.label}</label>
      <Slider
        value={props.value}
        name={props.name}
        min={props.min}
        max={props.max}
        step={props.step}
        onChange={onChangeFunction}
      />
    </div>
  )
}

export default RangeSliderWithLabel;