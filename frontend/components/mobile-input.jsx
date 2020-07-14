import React, { useState } from 'react'
import {MobileInput} from 'p2pu-components'

import 'p2pu-components/dist/build.css'

const SignupMobileInput = (props) => {
  const [ value, setValue ] = useState(props.phone)

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
      <MobileInput
        name="mobile"
        id="id_mobile"
        label={label}
        helpText={hint}
        placeholder="Enter phone number"
        value={props.phone}
        flagsImagePath="/static/images/flags.png"
        errorMessage={errorSpan}
      />
    );
}

export default SignupMobileInput