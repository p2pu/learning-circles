import React from 'react';

import { date, time} from 'p2pu-components/dist/utils/i18n';

import DelayedPostForm from './manage/delayed-post-form';

// TODO move to p2pu-components or i18n.js in frontend/helpers
/* Opinionated date format for learning circles */
export function meetingDateFormat(date_, locale){
  const options = { weekday: 'long', month: 'long', day: 'numeric' }
  return new Date(date_).toLocaleDateString(locale, options)
}


const RsvpForm = ({formData, updateForm}) => {
  const handleChange = rsvpValue => e => {
    e.preventDefault();
    updateForm({rsvp: rsvpValue});
  };
  return (
    <form>
      <p>{ formData.rsvp === null ? "Can you attend this meeting?" : `You RSVPed ${formData.rsvp?'yes':'no'}. Change your RSVP?`}</p>
      <button 
        onClick={handleChange(true)}
        className="btn p2pu-btn orange" 
      >yes</button> / <button 
        onClick={handleChange(false)}
        className="btn p2pu-btn orange"
      >no</button>
    </form>
  );
}


const Rsvp = props => {
  return (
    <div>
      { (props.rsvp && props.done) 
        && <p>You RSVPed {props.rsvp?'yes':'no'} for this meeting.</p>
      }
      { (!props.done && props.meetingId) &&
        <DelayedPostForm
          createObject={true}
          actionUrl="/api/rsvp/"
          initialValues={{rsvp: props.rsvp, meeting: props.meetingId}}
          onFormSubmitted={ updatedData => {} }
        >
          <RsvpForm/>
        </DelayedPostForm>
      }
    </div>
  );
};


const MeetingCard = props => {
  const {meeting_date, meeting_time} = props;
  const {rsvp} = props;
  const formattedDate = meetingDateFormat(meeting_date);
  const formattedTime = time(meeting_time);
  const done = new Date() > new Date(props.meeting_datetime);
  return (
    <div className={`item meeting ${done?'done':'todo'}`} id={`meeting-${props.id}`}>
      <div className="icon"></div>
      <div className="card">
        { (rsvp || !done) &&
          <button className={"card-collapse-toggle" + (done?' collapsed':'')} data-bs-toggle="collapse" data-bs-target={`#collapse-meeting-${props.id}`} type="button" aria-expanded={!done} aria-controls={`collapse-meeting-${props.id}`}><i className="fa fa-chevron-down"></i></button>
        }
        <div className="card-title">Meeting #{props.meeting_number}: {formattedDate}, {formattedTime}</div>
        
        { (rsvp || !done) &&
          <div class={"collapse" + (!done?'.show':'')} id={`collapse-meeting-${props.id}`}>
            <Rsvp rsvp={rsvp} meetingId={props.meeting_id} done={done}/>
          </div>
        }
      </div>
    </div>
  );
}

const MessageCard = props => {
  return (
    <div className="item message done" id={`meeting-${props.id}`}>
      <div className="icon"></div>
      <div className="card">
        <button className="card-collapse-toggle collapsed" data-bs-toggle="collapse" data-bs-target={`#collapse-meeting-${props.id}`} type="button" aria-expanded="false" aria-controls={`collapse-meeting-${props.id}`}><i className="fa fa-chevron-down"></i></button>
        <div className="card-title">Subject: {props.subject}</div>
        <div>Sent: {meetingDateFormat(props.sent_at)}</div>
        <div class="collapse" id={`collapse-meeting-${props.id}`}>
          <div class="email-preview p-2" dangerouslySetInnerHTML={{__html: props.body}}></div>
        </div>
      </div>
    </div>
  );
}

const SurveyCard = props => {
  return (
    <div className="item survey todo" id="survey">
      <div className="icon"></div>
      <div className="card">
        <button className="card-collapse-toggle" data-bs-toggle="collapse" data-bs-target="#collapse-survey" type="button" aria-expanded="true" aria-controls="collapse-survey"><i className="fa fa-chevron-down"></i></button>
        <div className="card-title">Reflect</div>
        <div class="collapse.show" id="collapse-survey">
          <p>Complete survey</p>
        </div>
      </div>
    </div>
  );
}

const dateCompare = (a, b) => {
  if (a < b)
    return -1;
  if (a > b)
    return 1;
  return 0;
}

const ParticipantDash = props => {
  const {meetings, messages, signup_message, survey_link} = props;
  //TODO meeting number assume meetings in date order
  let items = meetings.map( (meeting, i) => {
    return {
      component: MeetingCard,
      time: new Date(meeting.meeting_datetime),
      data: {meeting_number: i+1, ...meeting},
    };
  });

  items = [...items, ...messages.map(msg => {
    return {
      component: MessageCard,
      time: new Date(msg.sent_at),
      data: msg,
    };
  })];

  items = [
    ...items,
    {
      component: MessageCard,
      time: new Date(signup_message.sent_at),
      data: signup_message,
    }
  ];

  items.sort( (a, b) => dateCompare(a.time, b.time));

  console.log(items);
  return (
    <div className="lc-timeline">
      { 
        items.map( (item, i) => {
          return <item.component {...item.data} key={i} id={i} />
        })
      }
      <SurveyCard />
    </div>
  );
}

export default ParticipantDash;
