import React, { Component } from 'react';
import axios from 'axios';

export default class ImageUploader extends Component {

  constructor(props) {
    super(props);
    this.state = { image: this.props.image };
    this.onChange = (e) => this._onChange(e);
    this.onUploadFinished = (url) => this._onUploadFinished(url);
  }

  _onChange(e) {
    const file = e.currentTarget.files[0];
    const url = '/api/upload_image/';
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
      this.setState({ image: res.data.image_url })
      this.onUploadFinished(res.data.image_url)
    }).catch(err => {
      console.log(err)
    })
  }

  _onUploadFinished(url) {
    this.props.handleChange({ [this.props.name]: url })
  }

  render() {
    console.log('image uploader props', this.props)

    return(
      <div className={`input-with-label form-group ${this.props.classes}`}>
        <label htmlFor={this.props.name}>{this.props.label}</label>
        <input
          className='form-control'
          type='file'
          name={this.props.name}
          id={this.props.id}
          onChange={this.onChange}
        />
        {
          this.state.image &&
          <div className='image-preview' style={{ width: '250px'}}>
            <img src={this.state.image} alt='Image preview' style={{ width: '100%', height: '100%'}} />
          </div>
        }
      </div>
    )
  }
}
