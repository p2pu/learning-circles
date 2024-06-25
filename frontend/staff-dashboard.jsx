import React, {useState} from 'react'
import ReactDOM from 'react-dom'
import { createRoot } from 'react-dom/client';
import ErrorBoundary from './components/error-boundary'

import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


const ExportLinks = props => {

  const [requestPending, setRequestPending] = useState(false) // indicate that request to create export is pending
  const [pollingUrl, setPollingUrl] = useState('')
  const [exportUrl, setExportUrl] = useState('')
  const [errorMessage, setErrorMessage] = useState('')

  const startPolling = url => {
    setPollingUrl(url)

    const pollRequest = async backoff => {
      try {
        const pollResp = await axios({url, method: 'GET', responseType: 'json'});
        if (pollResp.status === 200) {
          const result = pollResp.data
          if (result.status == 'PENDING'){
            console.log(`done polling ${pollingUrl}, ${pollResp}`)
            setTimeout(pollRequest, backoff, backoff*2)
          } else if (result.status == 'SUCCESS') {
            console.log(`done polling ${pollingUrl}, ${pollResp}`)
            setPollingUrl('')
            setExportUrl(result.result.presigned_url)
            setRequestPending(false)
            return
          }
        }
      } catch (e) {
        setErrorMessage('Something went wrong while waiting for the result')
        console.log(e)
      }
    }

    pollRequest(5000)

  }

  const onClick = e => {
    e.preventDefault()
    const url = e.target.href
    // Post request and start polling
    setExportUrl('')
    setErrorMessage('')
    setRequestPending(true)
    axios({url, method: 'GET', responseType: 'json'}).then(res => {
      if (res.status === 200){
        console.log(res.data.task_id)
        console.log('Start polling')
        startPolling(`/en/export/status/${res.data.task_id}/`)
      } else {
        console.log('Export request returned unexpected status code', res)
        setErrorMessage('Something went wrong creating the export')
        setRequestPending(false)
      }
    }).catch(err => {
      console.log('Export request failed', err)
      setErrorMessage('Something went wrong creating the export')
      setRequestPending(false)
    })
  }

  return (
    <>
    <ul className="row list-unstyled">
      { 
        props.exportLinks.map( ({url, text}, index) => 
          <li key={index} className="col d-flex mb-3">
            <a className={"btn btn-primary w-100 " + (requestPending?"disabled":"") } href={url} onClick={onClick} ><i className="fas fa-download" aria-hidden="true"></i><br/>{text}</a>
          </li>
        )
      }
    </ul>
      { pollingUrl && <div><span className="spinner-border spinner-border-sm" role="status"></span>&nbsp;Busy creating export, don't refesh page</div>}
      { exportUrl && <a href={exportUrl}>Download your export</a> }
      { errorMessage && <div className="alert alert-danger">{errorMessage}</div> }
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

