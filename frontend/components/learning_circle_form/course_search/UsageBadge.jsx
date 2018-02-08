import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import ReactTooltip from 'react-tooltip'

const UsageBadge = ({ number, id }) => {
  const display = number > 0
  const pluralizedText = number === 1 ? 'learning circle' : 'learning circles';
  const icon = number === 1 ? 'done' : 'done_all';
  const tooltipText = `Used by ${number} ${pluralizedText}`;

  if (display) {
    return (
      <div className='usage-badge' data-tip data-for={id}>
        <div className='text'>
          <i className="material-icons">{icon}</i>{number}
          <ReactTooltip id={id} class="p2pu-tooltip" place="bottom" effect="solid" aria-haspopup='true'>
            <span>{tooltipText}</span>
          </ReactTooltip>
        </div>
      </div>
    );
  } else {
    return null
  }

}

export default UsageBadge
