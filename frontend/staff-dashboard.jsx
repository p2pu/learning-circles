import React, {useState} from 'react'
import ReactDOM from 'react-dom'
import { createRoot } from 'react-dom/client';
import ErrorBoundary from './components/error-boundary'

import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


/* TODO
 * - [ ] Feedback to show result is pending
 * - [ ] Pending result from backend
*/
const ExportLinks = props => {

  const [pollingUrl, setPollingUrl] = useState('');
  const [exportUrl, setExportUrl] = useState('');

  const startPolling = url => {
    setPollingUrl(url)

    const pollRequest = async backoff => {
      try {
        const pollResp = await axios({url, method: 'GET', responseType: 'json'});
        if (pollResp.status === 200) {
          console.log(`done polling ${pollingUrl}, ${pollResp}`)
          const result = pollResp.data
          if (result.status == 'PENDING'){
            setTimeout(pollRequest, backoff, backoff*2)
          } else if (result.status == 'SUCCESS') {
            setPollingUrl('')
            setExportUrl(result.result.presigned_url)
            return
          }
        }
      } catch (e) {
        // TODO, erm
        console.log(e)
      }
    }

    pollRequest(5000)

  }

  const onClick = e => {
    e.preventDefault()
    const url = e.target.href
    // Post request and start polling
    axios({url, method: 'GET', responseType: 'json'}).then(res => {
      if (res.status === 200){
        console.log(res.data.task_id)
        console.log('Start polling')
        startPolling(`/en/export/status/${res.data.task_id}/`)
      } else {
        // TODO
        console.log("error");
      }
    }).catch(err => {
      //TODO 
      console.log(err);
    })

  }

  return (
    <>
    <ul className="row list-unstyled">
      { 
        props.exportLinks.map( ({url, text}, index) => 
          <li key={index} className="col d-flex mb-3">
            <a className="btn btn-primary w-100" href={url} onClick={onClick} ><i className="fas fa-download" aria-hidden="true"></i><br/>{text}</a>
          </li>
        )
      }
    </ul>
      { exportUrl && <a href={exportUrl}>Download your export</a> }
    </>
  )
}

const reactDataEl = document.getElementById('react-data')
const reactData = JSON.parse(reactDataEl.textContent)

const element = document.getElementById('download-links')
const root = createRoot(element)
root.render(
  <ErrorBoundary scope="staff-dashboard">
    <ExportLinks {...reactData} />
  </ErrorBoundary>
)

