import React, { useState } from 'react'

import RatingInput from './manage/meeting-rating-input';
import MeetingReflectionInput from './manage/meeting-reflection-input';
import AttendanceInput from './manage/meeting-attendance-input';
import DelayedPostForm from './manage/delayed-post-form';


const MeetingFeedbackForm = props => {
  const {formData, updateForm} = props;
  return (
    <form>
      <RatingInput value={formData.rating} onChange={updateForm}/>
      <AttendanceInput formData={formData} onChange={updateForm}/>
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
