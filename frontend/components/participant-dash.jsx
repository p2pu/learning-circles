import React from 'react';
import { date, day, time } from 'p2pu-components/dist/utils/i18n';

const MeetingCard = props => {
  const {meeting_date, meeting_time} = props;
  const formattedDate = date(meeting_date, 'en-us');
  const formattedTime = time(meeting_time);
  const done = new Date() > new Date(props.meeting_datetime);
  return (
    <div className={`item meeting ${done?'done':'todo'}`} id={`meeting-${props.id}`}>
      <div className="icon"></div>
      <div className="card">
        <button className={"card-collapse-toggle" + (done?' collapsed':'')} data-bs-toggle="collapse" data-bs-target={`#collapse-meeting-${props.id}`} type="button" aria-expanded={!done} aria-controls={`collapse-meeting-${props.id}`}><i className="fa fa-chevron-down"></i></button>
        <div className="card-title">Meeting #{props.meeting_number}: {formattedDate} {formattedTime}</div>

        <div class="collapse" id={`collapse-meeting-${props.id}`}>
        </div>
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
        <div>Sent: {date(props.sent_at)}</div>
        <div class="collapse" id={`collapse-meeting-${props.id}`}>
          <div class="email-preview p-2" dangerouslySetInnerHTML={{__html: props.body}}></div>
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
  const {meetings, messages} = props;
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

  items.sort( (a, b) => dateCompare(a.time, b.time));

  console.log(items);
  return (
    <div className="lc-timeline">
      { 
        items.map( (item, i) => {
          return <item.component {...item.data} key={i} id={i} />
        })
      }
    </div>
  );
}

export default ParticipantDash;
