import React, { Component } from 'react';
import axios from 'axios';

export default class ImageUploader extends Component {

  constructor(props) {
    super(props);
    this.state = {};
    this.onChange = (e) => this._onChange(e);
    this.onUploadFinished = (id) => this.onUploadFinished(id);
  }

  _onChange(e) {
    const file = e.currentTarget.files[0];
    const url = '/en/upload_image/';
    const data = new FormData();

    data.append('image', file)

    axios({
      url,
      data,
      method: 'post',
      responseType: 'json',
      config: { headers: {'Content-Type': 'multipart/form-data' }}
    }).then(res => {
      console.log(res)
    }).catch(err => {
      console.log(err)
    })
  }

  _onUploadFinished(id) {
    this.props.handleChange({ [this.props.name]: id })
  }

  render() {
    return(
      <div className={`input-with-label form-group ${this.props.classes}`}>
        <label htmlFor={this.props.name}>{this.props.label}</label>
        <input
          className='form-control'
          type='file'
          name={this.props.name}
          id={this.props.id}
          onChange={this.onChange}
          value={this.props.value}
        />
      </div>
    )
  }
}
