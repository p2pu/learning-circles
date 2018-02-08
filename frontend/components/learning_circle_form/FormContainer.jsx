import React from 'react'
import FormTabs from './FormTabs'
import ActionBar from './ActionBar'

const FormContainer = (props) => {

  const hide = props.showHelp ? 'show-help' : 'hide-help';

  return (
    <div className={`form-container ${hide}`}>
      <FormTabs { ...props } />
      <ActionBar { ...props} />
    </div>
  );
}

export default FormContainer;