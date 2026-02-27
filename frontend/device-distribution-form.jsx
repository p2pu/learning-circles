import React, {useState} from 'react'
import ReactDOM from 'react-dom'

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

