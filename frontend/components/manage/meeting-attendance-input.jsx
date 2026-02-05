import React, { useState } from 'react'

const SummarizedAttendanceInput  = ({value, onChange}) => 
  <div id="div_id_attendance" className="form-group">
    <label htmlFor="id_attendance" className="col-form-label">How many people attended?</label> 
    <div>
      <input type="number" name="attendance" min="0" className="numberinput form-control form-control form-control" value={value} onChange={e => onChange({'attendance': e.target.value})} id="id_attendance" /> 
    </div> 
  </div>;


const GranularAttendanceInput = ({value, onChange, learners}) => {
  var parsedValue = JSON.parse(value || '{}')

  const handleCheck = userId => {
    if (parsedValue[userId]) {
      delete parsedValue[userId]
    } else {
      parsedValue[userId] = true
    }
    onChange({"granular_attendance": JSON.stringify(parsedValue)})
  }

  return (
    <div id="div_id_granular_attendance" className="form-group">
      <label htmlFor="id_granular_attendance" className="col-form-label">Who attended?</label> 
      {
        learners.map(user => (
          <div className="form-check" key={user.id}>
            <input className="form-check-input" type="checkbox" value="" id="checkChecked" checked={parsedValue[user.id]} onChange={e => handleCheck(user.id)}/>
            <label className="form-check-label" htmlFor="checkChecked">
              {`${user.name} <${user.email || user.mobile}>`}
            </label>
          </div>
        ))
      }
    </div>
  );
}

const AttendanceInput = ({formData, onChange}) => {

  const [summarizedInput, setSummarizedInput] = useState(
    !(formData.granular_attendance && formData.granular_attendance.length > 2)
  )

  const toggle = (e) => {
    e.preventDefault()
    setSummarizedInput(!summarizedInput)
  }

  return (
    <>
      { summarizedInput && (
        <>
        <SummarizedAttendanceInput value={formData.attendance} onChange={onChange} /> 
        <p>(<a href="#" onClick={toggle} >Record per learner attendance</a>)</p>
        </>
      )}
      { !summarizedInput && (
        <>
        <GranularAttendanceInput 
          value={formData.granular_attendance}
          onChange={onChange}
          learners={window.learners}
        />
        <p>(<a href="#" onClick={toggle} >Record summarized attendance</a>)</p>
      </>
      )}
    </>
  );
}

export default AttendanceInput;
