import React from 'react'
import ReactDOM from 'react-dom'
import ErrorBoundary from './components/error-boundary'

import { createRoot } from 'react-dom/client';

/* TODO
 * - [ ] intercept clicking on link
 * - [ ] store task id back
 * - [ ] poll result
 * - [ ] display download link when ready
*/
const ExportLinks = props => {
  return (
    <ul className="row list-unstyled">
      { 
        props.exportLinks.map( ({url, text}, index) => 
          <li key={index} className="col d-flex mb-3"><a className="btn btn-primary w-100" href={url} ><i className="fas fa-download" aria-hidden="true"></i><br/>{text}</a></li>
        )
      }
    </ul>
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

