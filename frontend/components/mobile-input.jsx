import React from 'react'
import ReactTelInput from 'react-telephone-input'

require('./stylesheets/mobile-input.scss');

export default class MobileInput extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      phone: props.value
    };
  }

  cleanFormatting(phoneNumber){
    const num = phoneNumber.replace(/[()\ -]/g, '');
    if (num.length <= 4) {
      return '';
    }
    return num;
  }

  render() {
    const {label, hint, error} = this.props;
    let errorSpan = null;
    if (error) {
      errorSpan = (
        <span id="error_1_id_mobile" className="invalid-feedback"><strong>{error}</strong></span>
      );
    }
    return (
      <div>
        <label htmlFor="id_mobile" className="control-label ">{label}</label>
        <div className="controls "> 

          <ReactTelInput
            placeholder="Enter phone number"
            flagsImagePath="/static/images/flags.png"
            value={ this.state.phone }
            onChange={ phone => this.setState({ phone }) }
            defaultCountry="us" />
          <input id="id_mobile" class={error && "form-control is-invalid" || "form-control"} type="hidden" name="mobile" value={this.cleanFormatting(this.state.phone)} />
          {errorSpan}

          <small id="hint_id_mobile" class="form-text text-muted">{hint}</small> 
        </div> 
      </div>
    );
  }
}
