import React, { useState } from 'react'

const CharacterCountInput = props => {

  const [value, setValue] = useState(props.value || '');
  const invalid = !!props.error || (value.length > props.maxLength);

  return(
    <span>
      <input type="hidden" value={value} name={props.name} />
      <textarea
        name="character_count_input"
        rows="3"
        className={"textinput textInput form-control" + (invalid?' is-invalid':'')}
        value={value}
        onChange={e => setValue(e.currentTarget.value) }
      />
      <p>{value.length}/{props.maxLength}</p>
    </span>
  );
}

export default CharacterCountInput;
