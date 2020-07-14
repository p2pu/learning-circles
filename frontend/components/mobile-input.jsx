import React, { useState } from 'react'
import {MobileInput} from 'p2pu-components'

import 'p2pu-components/dist/build.css'

const SignupMobileInput = (props) => {
  const [ value, setValue ] = useState(props.value)

  const cleanFormatting = (phoneNumber) => {
    const num = phoneNumber.replace(/[()\ -]/g, '');
    if (num.length <= 4) {
      return '';
    }
    return num;
  }

    const {label, hint, error} = props;
    let errorSpan = null;
    if (error) {
      errorSpan = (
        <span id="error_1_id_mobile" className="invalid-feedback"><strong>{error}</strong></span>
      );
    }
  return (
    <div>
      <input id="id_mobile" type="hidden" name="mobile" value={cleanFormatting(value)} />
      <MobileInput
        name="mobileBOB"
        id="id_mobileBOB"
        label={label}
        helpText={hint}
        placeholder="Enter phone number"
        value={props.phone}
        handleChange={({mobileBOB}) => setValue(mobileBOB)}
        flagsImagePath="/static/images/flags.png"
        errorMessage={errorSpan}
      />
    </div>
    );
}

export default SignupMobileInput
