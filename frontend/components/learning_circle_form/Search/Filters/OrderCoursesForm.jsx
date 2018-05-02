import React from 'react'
import { SwitchWithLabels } from 'p2pu-input-fields'


const OrderCoursesForm = (props) => {
  const formValues = {
    true: {
      label: 'Use in learning circles',
      value: 'usage'
    },
    false: {
      label: 'Course title',
      value: 'title'
    }
  }

  const handleSelect = (value) => {
    const order = formValues[value].value
    props.updateQueryParams({ order })
  }

  const defaultChecked = props.order && props.order === formValues.true.value;

  return(
    <SwitchWithLabels
      name="order-courses"
      labelRight={formValues.true.label}
      labelLeft={formValues.false.label}
      onChange={handleSelect}
      defaultChecked={defaultChecked}
    />
  )
}

export default OrderCoursesForm;
