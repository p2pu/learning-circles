import React from 'react';

import { date, time} from 'p2pu-components/dist/utils/i18n';

import DelayedPostForm from './manage/delayed-post-form';

// TODO move to p2pu-components or i18n.js in frontend/helpers
/* Opinionated date format for learning circles */
export function meetingDateFormat(date_, locale){
  const options = { weekday: 'long', month: 'long', day: 'numeric' }
  // Append time to make sure that the date is interpreted as givin in local time rather than UTC
  // see https://maggiepint.com/2017/04/11/fixing-javascript-date-web-compatibility-and-reality/
  return new Date(date_ + "T00:00").toLocaleDateString(locale, options)
}


const RsvpForm = ({formData, updateForm}) => {
  const handleChange = e => {
    updateForm({rsvp: e.target.value === "yes"});
  };
  return (
    <form>
      <p>Will you attend this meeting?</p>
      <div className="form-check">
        <input 
          className="form-check-input"
          type="radio" name="rsvp" value="yes" id="rsvpYes"
          onChange={handleChange}
          checked={formData.rsvp}
        />
        <label className="form-check-label" htmlFor="rsvpYes">Yes</label>
      </div>
      <div className="form-check">
        <input 
          className="form-check-input"
          type="radio" name="rsvp" value="no" id="rsvpNo"
          onChange={handleChange}
          checked={formData.rsvp === false}
        />
        <label className="form-check-label" htmlFor="rsvpNo">No</label>
      </div>
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
          createObject={props.rsvp === undefined}
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
          <button 
            className={"card-collapse-toggle" + (done?' collapsed':'')}
            data-bs-toggle="collapse"
            data-bs-target={`#collapse-meeting-${props.id}`}
            type="button"
            aria-expanded={!done} 
            aria-controls={`collapse-meeting-${props.id}`}
          >
            <i className="fa fa-chevron-down"></i>
          </button>
        }
        <div className="card-title">Meeting #{props.meeting_number}: {formattedDate}, {formattedTime}</div>
        
        { (rsvp || !done) &&
          <div className={"collapse" + (!done?' show':'')} id={`collapse-meeting-${props.id}`}>
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
        <button 
          className="card-collapse-toggle collapsed"
          data-bs-toggle="collapse"
          data-bs-target={`#collapse-meeting-${props.id}`}
          type="button"
          aria-expanded="false"
          aria-controls={`collapse-meeting-${props.id}`}
        >
          <i className="fa fa-chevron-down"></i>
        </button>
        <div className="card-title">Subject: {props.subject}</div>
        <div>
          Sent: {
            new Date(props.sent_at).toLocaleDateString(
              undefined,
              { weekday: 'long', month: 'long', day: 'numeric' }
            )
          }&nbsp;at&nbsp;
          { 
            new Date(props.sent_at).toLocaleTimeString(
              undefined,
              {hour: 'numeric', minute: '2-digit'}
            )
          }
        </div>
        <div className="collapse" id={`collapse-meeting-${props.id}`}>
          <div className="email-preview p-2" dangerouslySetInnerHTML={{__html: props.body}}></div>
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
        <button
          className="card-collapse-toggle"
          data-bs-toggle="collapse"
          data-bs-target="#collapse-survey"
          type="button"
          aria-expanded="true"
          aria-controls="collapse-survey"
        >
          <i className="fa fa-chevron-down"></i>
        </button>
        <div className="card-title">Reflect</div>
        { props.survey_completed &&
          <div className="collapse show" id="collapse-survey">
            <p>Thank you for completing the survey.</p>
          </div>
        }
        { !props.survey_completed &&
          <div className="collapse show" id="collapse-survey">
            <p>Please complete this <a href={props.survey_link}>short survey</a>. Your feedback will help your facilitator and P2PU improve future learning circles.</p>
          </div>
        }
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

function facilitatorDisplay(facilitators){
  if (facilitators.length == 1)
    return facilitators[0];
  if (facilitators.length == 2)
    return `${facilitators[0]} and ${facilitators[1]}`;
  if (facilitators.length > 2)
    return `${facilitators.slice(0,-1).join(', ')} and ${facilitators[facilitators.length-1]}`;
}

const InfoCard = props => {
  const {learning_circle} = props;
  const {course} = learning_circle;
  return (
    <div className="item info" id="info">
      <div className="icon"></div>
      <div className="card">
        <button
          className="card-collapse-toggle"
          data-bs-toggle="collapse"
          data-bs-target="#collapse-info"
          type="button"
          aria-expanded="true"
          aria-controls="collapse-info"
        >
          <i className="fa fa-chevron-down"></i>
        </button>
        <div className="card-title">You've signed up as {props.application.name} &lt;{props.application.email}&gt;</div>
        <div className="collapse show" id="collapse-info">
          <p>This learning circle is facilitated by {facilitatorDisplay(learning_circle.facilitators)}</p>
          <p>Course materials provided by <a href={course.link} target="_blank">{course.provider}</a></p>
          <p>Taking place at { !!learning_circle.venue_website && <a href="{learning_circle.venue_website}">{ learning_circle.venue }</a>}{ !learning_circle.venue_website && learning_circle.venue}, {learning_circle.venue_address}</p>
          <p></p>
        </div>
      </div>
    </div>
  );
}

const CuCreditPrompt = props => {
  return (
    <div className="item credit" id="info">
      <div className="icon"></div>
      <div className="card">
        <p>Participants in this learning circle have the option to earn college credit from College Unbound. In order to earn credit, you must complete a learning journal while participating in the learning circle. For more information, <a href="https://docs.p2pu.org/frequently-asked-questions#credit-bearing-faqs">refer to the FAQs</a>.</p>
      </div>
    </div>
  );
}


const DDDeviceForm = props => {
  const done = props.device_agreement_completed
  return (
    <div className={`item device-form ${done?'done':'todo'}`} id="device-form">
      <div className="icon"></div>
      <div className="card">
        <button
          className={`card-collapse-toggle ${done?' collapsed':''}`}
          data-bs-toggle="collapse"
          data-bs-target="#collapse-device-agreement"
          type="button"
          aria-expanded={!done} 
          aria-controls="collapse-device-agreement"
        >
          <i className="fa fa-chevron-down"></i>
        </button>
        <div className="card-title">Device Agreement</div>
        { done &&
          <div className="collapse" id="collapse-device-agreement">
            <p>Thank you for completing your device agreement form.</p>
            <p><a href={props.device_agreement_url} className="p2pu-btn btn btn-primary">Update details</a></p>
          </div>
        }
        { !done &&
          <div className="collapse show" id="collapse-device-agreement">
            <p>This enrollment form serves as your authorization to receive a device from Digital Skills Detroit. Please complete within your first 2 Digital Skills Detroit sessions to be considered for your device upon program completion.</p> 
            <p><a href={props.device_agreement_url} className="p2pu-btn btn btn-primary">Complete enrollment form</a></p>
          </div>
        }
      </div>
    </div>
  );

}


const ParticipantDash = props => {
  const {meetings, messages, signup_message, survey_link, survey_completed} = props;

  let items = [
    ...meetings.map( (meeting, i) => {
      return {
        component: MeetingCard,
        time: new Date(meeting.meeting_datetime),
        data: {meeting_number: i+1, ...meeting}, // TODO meeting number assume meetings are already in date order
      };
    }),
    ...messages.map(msg => {
      return {
        component: MessageCard,
        time: new Date(msg.sent_at),
        data: msg,
      };
    }),
    {
      component: MessageCard,
      time: new Date(signup_message.sent_at),
      data: signup_message,
    }
  ];

  items.sort( (a, b) => dateCompare(a.time, b.time));

  return (
    <div className="lc-timeline">
      <InfoCard {...props} />
      { props.cu_credit && <CuCreditPrompt {...props}/>}
      { props.device_agreement_url && <DDDeviceForm {...props} /> }
      { 
        items.map( (item, i) => {
          return <item.component {...item.data} key={i} id={i} />
        })
      }
      <SurveyCard {...{survey_link, survey_completed}} />
    </div>
  );
}

export default ParticipantDash;
