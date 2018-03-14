import React, { Component } from 'react';
import ApiHelper from '../../helpers/ApiHelper';

export default class ImageUploader extends Component {

  constructor(props) {
    super(props);
    this.state = { image: this.props.image };
    this.onChange = (e) => this._onChange(e);
  }

  _onChange(e) {
    const file = e.currentTarget.files[0];
    const data = new FormData();
    data.append('image', file)

    const onSuccess = (data) => {
      this.setState({ image: data.image_url });
      this.props.handleChange({ [this.props.name]: data.image_url })
    }

    const onError = (data) => {
      console.log(data.errors)
      this.props.handleChange({ [this.props.name]: null })
    }

    const onFail = (err) => {
      console.log(err)
    }

    const config = { headers: {'Content-Type': 'multipart/form-data' }}
    const opts = { data, config, onSuccess, onError, onFail };
    const api = new ApiHelper('images');

    api.createResource(opts);
  }

  render() {
    return(
      <div className={`input-with-label form-group ${this.props.classes}`}>
        <label htmlFor={this.props.name}>{this.props.label}</label>
        <input
          className='image-upload'
          type='file'
          name={this.props.name}
          id={this.props.id}
          onChange={this.onChange}
        />
        {
          this.props.errorMessage &&
          <div className='error-message'>
            { this.props.errorMessage }
          </div>
        }
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
