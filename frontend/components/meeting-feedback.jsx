import React, { useState } from 'react'

import RatingInput from './manage/meeting-rating-input';
import MeetingReflectionInput from './manage/meeting-reflection-input';
import DelayedPostForm from './manage/delayed-post-form';

const GranularAttendanceInput = ({value, onChange, learners}) => {

  var parsedValue = JSON.parse(value)

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

const AttendanceInput = ({value, onChange}) => 
  <div id="div_id_attendance" className="form-group">
    <label htmlFor="id_attendance" className="col-form-label">How many people attended?</label> 
    <div>
      <input type="number" name="attendance" min="0" className="numberinput form-control form-control form-control" value={value} onChange={e => onChange({'attendance': e.target.value})} id="id_attendance" /> 
    </div> 
  </div>;


const MeetingFeedbackForm = props => {
  const {formData, updateForm} = props;
  return (
    <form>
      <RatingInput value={formData.rating} onChange={updateForm}/>
      <GranularAttendanceInput 
        value={formData.granular_attendance}
        onChange={updateForm}
        learners={window.learners}
      />
      <AttendanceInput value={formData.attendance} onChange={updateForm}/>
      <MeetingReflectionInput value={formData.reflection} onChange={updateForm} />
    </form>
  )
}


const MeetingFeedback = props => {
  const {meetingId} = props;
  const [panelCollapsed, setPanelCollapsed] = useState(!!props.feedbackId);
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [actionUrl, setActionUrl] = useState(props.actionUrl);
  const [createObject, setCreateObject] = useState(!props.feedbackId);

  let itemState = formSubmitted?'done':props.itemState;
  let initialFormValues = {
    rating: props.rating,
    attendance: props.attendance,
    granular_attendance: props.granularAttendance,
    reflection: props.reflection,
    study_group_meeting: props.meetingId,
  };

  let panelCollapseClass = panelCollapsed?" collapse":"";

  return (
    <div className={"meeting-item" + (itemState?` ${itemState}`:'')}>
      <p>Reflect and share feedback {props.feedbackId && <span>(<a data-bs-toggle="collapse" href={`#meeting-${meetingId}-feedback`} role="button" aria-expanded="true" aria-controls={`meeting-${meetingId}-feedback`}>view</a>)</span>}
      </p>
      { props.showForm &&
          <div 
            className={ "meeting-item-details" + panelCollapseClass } 
            id={`meeting-${meetingId}-feedback`}
          >
            <p>Your reflections help P2PU identify common themes for upcoming facilitator calls (<a href="https://community.p2pu.org/c/community-events/upcoming-events/79" target="_blank">RSVP here</a>). Your responses will be shared with P2PU (and your team if you are part of one).</p>

            <DelayedPostForm
              createObject={createObject}
              actionUrl={actionUrl}
              initialValues={initialFormValues}
              onFormSubmitted={()=>setFormSubmitted(true)}
              onObjectCreated={object => { setActionUrl(object.url); setCreateObject(false); } }
            >
              <MeetingFeedbackForm/>
            </DelayedPostForm>
          </div>
      }
    </div>
  );
};

export default MeetingFeedback;
