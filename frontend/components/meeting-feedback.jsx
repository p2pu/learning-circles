import React, { useState } from 'react'
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const RatingInput = props => {
  const {rating, setRating} = props;
  const ratingOptions = [
    [5, 'Great', "/static/images/icons/p2pu-joy-bot.svg"],
    [4, 'Pretty well', "/static/images/icons/p2pu-happy-bot.svg"],
    [3, 'Okay', "/static/images/icons/p2pu-meh-bot.svg"],
    [2, 'Not so good', "/static/images/icons/p2pu-sad-bot.svg"],
    [1, 'Awful', "/static/images/icons/p2pu-neon-tear-bot.svg"],
  ];

  return (
    <div id="div_id_rating" className="form-group">
      <p><label htmlFor="id_rating" className="col-form-label  requiredField">Overall, how did this meeting go?</label></p>
      <div className="p2pu-bot-selector">
        { ratingOptions.map(option => 
          <label key={option[0]}>
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
  );
}

const AttendanceInput = ({attendance, setAttendance}) => 
  <div id="div_id_attendance" className="form-group">
    <label htmlFor="id_attendance" className="col-form-label">How many people attended?</label> 
    <div>
      <input type="number" name="attendance" min="0" className="numberinput form-control form-control form-control" value={attendance} onChange={e => setAttendance(e.target.value)} id="id_attendance" /> 
    </div> 
  </div>;


const MeetingFeedback = props => {
  const {meetingId, postUrl} = props;

  const [rating, setRating] = useState(props.rating);
  const [attendance, setAttendance] = useState(props.attendance);

  // first prompt is a legacy prompt and should only be used if the reflection value doesn't 
  // indicate a prompt index + prompt
  const reflectionPrompts = [
    'Anything else you want to share?',
    'What surprised you during this meeting?',
    'What did you find new and refreshing?',
    'What feels most challenging right now?',
    'What delighted you?',
    'What made you laugh?',
    'What advice would you give another facilitator who wanted to use this material?',
  ];
  const randi = Math.floor(1 + Math.random()*(reflectionPrompts.length-1));
  let {
    reflection : initialReflection = JSON.stringify({"promptIndex": randi, "prompt": reflectionPrompts[randi],}) 
  } = props;
  try {
    initialReflection = JSON.parse(initialReflection);
  } catch (error){
    initialReflection = {
      answer: props.reflection,
      promptIndex: 0,
      prompt: reflectionPrompts[0],
    }
  }

  const [reflection, setReflection] = useState(initialReflection);

  const cyclePrompt = e => {
    e.preventDefault();
    let newIndex = 1 + reflection.promptIndex%(reflectionPrompts.length-1);
    console.log(newIndex);
    setReflection({
      ...reflection,
      "promptIndex": newIndex, 
      "prompt": reflectionPrompts[newIndex]}
    );
  } 

  return (
    <>
    <form>
      <RatingInput rating={rating} setRating={setRating}/>
      <AttendanceInput attendance={attendance} setAttendance={setAttendance}/>

      <input type="hidden" name="reflection" value={reflection.answer?JSON.stringify(reflection):""}/>
      <div id="div_id_reflection" className="form-group">
        <label htmlFor="id_reflection" className="col-form-label">{reflectionPrompts[reflection.promptIndex]} (<a href="#" onClick={cyclePrompt} >Give me another question</a>)</label>
        <div>
          <textarea name="reflection_answer" rows="3" className="textarea form-control form-control form-control" id="id_reflection" value={reflection.answer} onChange={ e => setReflection({...reflection, 'answer': e.target.value}) }/>
        </div> 
      </div>
       
    </form>
    </>
  )
}

const DelayedPostForm = props => {
  const {actionUrl} = props;

  const [formData, setFormData] = useState({});
  const [pendingChanges, setPendingChanges] = useState(false);
  const [isPosting, setIsPosting] = useState(false);

  let timer = useRef();
  const postData = (delay=3000) => {
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => {
      setIsPosting(true);
      const data = new FormData();
      for (const key in formData) {
        data.append(key, formData[key]);
      }
      axios.post(actionUrl, data).then(res => {
        setIsPosting(false)
        if (res.status === 200) {
          setPendingChanges(false);
          console.log('updated course rating');
        } else {
          // TODO
          console.log("error saving course rating");
        }
      }).catch(err => {
        setIsPosting(false)
        //TODO 
        console.log(err);
      })
    }, delay);
  }

  const updateForm = (data, delay=3000) => {
    setFormData({...formData, ...data});
    postData(delay);
  }

  return (
    <div>
      <MeetingFeedback
        {...props}
        pendingChanges={pendingChanges}
        isPosting={isPosting}
        updateForm={updateForm}
        formData={formData}
      />
      { pendingChanges && !isPosting && <span> pending updates</span> }
      { isPosting && <><div className="spinner-border spinner-border-sm" role="status"><span className="sr-only">saving...</span></div><span> saving changes</span></> }
      { !pendingChanges && "changes saved" }
    </div>
  );
}

export default MeetingFeedback;

