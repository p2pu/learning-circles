import React, { Component } from 'react'
import axios from 'axios';
import moment from 'moment-timezone';

import { compact, uniqBy, sortBy } from 'lodash';
import Select from 'react-select';
import css from 'react-select/dist/react-select.css';


export default class TimeZoneSelect extends Component {
  constructor(props) {
    super(props);
    this.state = { value: this.props.timezone };
    this.onChange = (s) => this._onChange(s);
    this.detectTimeZone = () => this._detectTimeZone();
  }

  componentDidMount() {
    this.detectTimeZone()
  }

  _onChange(selected) {
    const timezone = !!selected ? selected.value : null;
    this.props.handleChange({ timezone });
    this.setState({ value: selected });
  }

  _detectTimeZone() {
    if (!!this.props.timezone) {
      this.setState({ value: { value: this.props.timezone, label: this.props.timezone } })
    } else if (!!this.props.latitude && !!this.props.longitude) {
      const url = `https://secure.geonames.org/timezoneJSON?lat=${this.props.latitude}&lng=${this.props.longitude}&username=p2pu`

      axios.get(url).then(res => {
        const timezone = res.data.timezoneId;
        this.props.handleChange({ timezone })
        this.setState({ value: { value: timezone, label: timezone } })
      }).catch(err => console.log(err))
    } else {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
      this.props.handleChange({ timezone })
      this.setState({ value: { value: timezone, label: timezone } })
    }
  }


  render() {
    const timezoneOptions = moment.tz.names().map((tz) => ({value: tz, label: tz }))

    return(
      <div>
        <Select
          name={ this.props.name }
          className='form-group input-with-label'
          value={ this.state.value }
          onChange={ this.onChange }
          options={timezoneOptions}
          name={'timezone'}
          id={'id_timezone'}
        />
        {
          this.props.errorMessage &&
          <div className="error-message minicaps">{this.props.errorMessage}</div>
        }
      </div>
    )
  }
}
