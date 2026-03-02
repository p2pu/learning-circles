import React, {useState} from 'react'
import ReactDOM from 'react-dom'

import MobileInput from './components/mobile-input'
import { AddressAutofill } from '@mapbox/search-js-react';

const AddressInput = props => {
  const [address, setAddress] = useState(props.address)

  return (
    <AddressAutofill
      accessToken={props.accessToken}
      options={{
        language: 'en',
        country: 'US'
      }}
      onRetrieve={e=> {
        console.log(e)
        console.log(e.features[0].properties)
        const newAddr = e.features[0].properties
        setAddress(newAddr.address_line1)
      }}
    >
      <input type="text" className="form-control textinput" required="" onChange={e=>setAddress(e.target.value )} autoComplete="address-line1" value={address} />
      <input type="hidden" name="address_line1" value={address} />
    </AddressAutofill>
  );
}


const reactDataEl = document.getElementById('react-data');
const reactData = JSON.parse(reactDataEl.textContent);
const input = document.querySelector('#id_address_line1')
const addressLine1 = input.value
const newInput = document.createElement("div")
ReactDOM.render(<AddressInput accessToken={reactData.MAPBOX_TOKEN} address={addressLine1} />, newInput)
input.replaceWith(newInput)


const element = document.getElementById('div_id_mobile');
if (element) {
  let label = element.querySelector('label');
  let hint = element.querySelector('#div_id_mobile .form-text');
  let error = element.querySelector('#error_1_id_mobile');
  let input = element.querySelector('#id_mobile');

  ReactDOM.render(
    <MobileInput
      label={label.textContent}
      hint={hint?hint.textContent:null}
      error={error?error.textContent:null}
      value={input.value}
    />,
    document.getElementById('div_id_mobile')
  );
}
