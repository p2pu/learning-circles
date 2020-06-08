import React from 'react'
import { InputWithLabel } from 'p2pu-components'

Location

const UrlInput = (props) => {
  const addProtocol = (e) => {
    let url = e[props.name];
    if (url.length >= 5 && url.substr(0,5) != 'https' && url.substr(0,5) != 'http:'){
      return props.handleChange({[props.name]: 'http://' + url});
    }
    return props.handleChange(e);
  };
  return (
    <InputWithLabel
      label={props.label}
      value={props.value}
      placeholder={props.placeholder}
      handleChange={addProtocol}
      name={props.name}
      id={props.id}
      errorMessage={props.errorMessage}
    />
  );
}

export default UrlInput;

