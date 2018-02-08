import { API_ENDPOINTS } from '../constants';
import { compact } from 'lodash';
import jsonp from 'jsonp';
import axios from 'axios';

export default class ApiHelper {
  constructor(resourceType) {
    this.resourceType = resourceType;
    this.baseUrl = API_ENDPOINTS[resourceType].baseUrl;
    this.validParams = API_ENDPOINTS[resourceType].searchParams;
  }

  generateUrl(params) {
    const baseUrl = this.baseUrl;
    const encodedParams = this.validParams.map((key) => {
      const value = params[key];
      if (!!value) {
        return `${key}=${encodeURIComponent(value)}`
      }
    })
    const queryString = compact(encodedParams).join('&');

    console.log('url', `${baseUrl}${queryString}`)
    return `${baseUrl}${queryString}`
  }

  fetchResource(opts) {
    const url = this.generateUrl(opts.params)

    jsonp(url, null, (err, data) => {
      if (err) {
        console.log(err)
      } else {
        console.log(data)
        opts.callback(data, opts)
      }
    })
  }

  createResource(opts) {
    const url = API_ENDPOINTS[this.resourceType].postUrl;
    const data = opts.data;

    axios({
      url,
      data,
      method: 'post',
      responseType: 'json',
      config: { headers: {'Content-Type': 'application/json' }}
    }).then(res => {
      if (res.data.status === 'created') {
        opts.onSuccess(res.data)
      } else if (res.data.errors) {
        opts.onError(res.data)
      }
    }).catch(err => {
      console.log(err)
      opts.onFail(err)
    })
  }
}