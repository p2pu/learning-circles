import React, { useState } from 'react'

import 'components/stylesheets/meeting-feedback.scss'

const MeetingFeedback = props => {
  const {meetingId} = props;

  const [rating, setRating] = useState(props.rating)
  const ratingOptions = [
    [5, 'Great', "/static/images/icons/p2pu-joy-bot.svg"],
    [4, 'Pretty well', "/static/images/icons/p2pu-happy-bot.svg"],
    [3, 'Okay', "/static/images/icons/p2pu-meh-bot.svg"],
    [2, 'Not so good', "/static/images/icons/p2pu-sad-bot.svg"],
    [1, 'Awful', "/static/images/icons/p2pu-neon-tear-bot.svg"],
  ];

  const [attendance, setAttendance] = useState(props.attendance);

  const reflectionPrompts = [
    'What surprised you during this meeting?',
    'What did you find new and refreshing?',
    'What feels most challenging right now?',
    'What delighted you?',
    'What made you laugh?',
    'What advice would you give another facilitator who wanted to use this material?',
  ];
  // TODO need to store both prompt and answer. And when answer
  const [promptIndex, setPromptIndex] = useState(Math.floor(Math.random()*reflectionPrompts.length));
  const [reflection, setReflection] = useState(props.reflection);

  const submitForm = (e) => {
    e.preventDefault();
  }

  return (
    <>
    <form action="/en/studygroup/1547/meeting/9636/feedback/create/" method="POST" onSubmit={submitForm}>

      <div id="div_id_rating" class="form-group">
        <p>
          <label htmlFor="id_rating" class="col-form-label  requiredField">Overall, how did this meeting go?</label></p>
          <div className="p2pu-bot-selector">
            { ratingOptions.map(option => 
              <label className="" key={option[0]}>
                <input 
                  type="radio"
                  name="rating"
                  value={option[0]}
                  onChange={e => setRating(e.target.value)}
                  checked={rating==option[0]?true:null}
                />
                <img src={option[2]} />
                <div className="text-center">{option[1]}</div>
              </label>
            )}
          </div>
      </div>

      <div id="div_id_attendance" class="form-group">
        <label htmlFor="id_attendance" class="col-form-label">How many people attended?</label> 
        <div>
          <input type="number" name="attendance" min="0" class="numberinput form-control form-control form-control" value={attendance} onChange={e => setAttendance(e.target.value)} id="id_attendance" /> 
        </div> 
      </div>

      <div id="div_id_reflection" class="form-group">
        <label htmlFor="id_reflection" class="col-form-label">{reflectionPrompts[promptIndex]} (<a href="#" onClick={e => { e.preventDefault(); setPromptIndex((promptIndex+1)%reflectionPrompts.length) } }>Give me another question</a>)</label>
        <div>
          <textarea name="reflection" rows="3" class="textarea form-control form-control form-control" id="id_reflection" value={reflection} onChange={ e => setReflection(e.target.value) }/>
        </div> 
      </div>
      <p><button type="submit" class="p2pu-btn btn-primary">Submit</button></p>
    </form>
    </>
  )
}

export default MeetingFeedback;

