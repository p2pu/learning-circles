import React, { useState, useRef } from 'react'
import axios from 'axios'

import RatingInput from './manage/meeting-rating-input';

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


const AttendanceInput = ({value, onChange}) => 
  <div id="div_id_attendance" className="form-group">
    <label htmlFor="id_attendance" className="col-form-label">How many people attended?</label> 
    <div>
      <input type="number" name="attendance" min="0" className="numberinput form-control form-control form-control" value={value} onChange={e => onChange({'attendance': e.target.value})} id="id_attendance" /> 
    </div> 
  </div>;


const ReflectionInput = ({value, onChange}) => {
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
  let initialReflection = value;
  if (initialReflection) {
    try {
      initialReflection = JSON.parse(value);
    } catch (error){
      initialReflection = {
        answer: value,
        promptIndex: 0,
        prompt: reflectionPrompts[0],
      }
    }
  } else {
    const randi = Math.floor(1 + Math.random()*(reflectionPrompts.length-1));
    initialReflection = {"promptIndex": randi, "prompt": reflectionPrompts[randi]};
  }

  const [reflection, setReflection] = useState(initialReflection);

  const cyclePrompt = e => {
    e.preventDefault();
    let newIndex = 1 + reflection.promptIndex%(reflectionPrompts.length-1);
    let updatedReflection = {
      ...reflection,
      "promptIndex": newIndex, 
      "prompt": reflectionPrompts[newIndex]
    };
    setReflection(updatedReflection);
    if (reflection.answer){
      onChange({reflection: JSON.stringify(updatedReflection)});
    }
  }

  const handleChange = e => {
    let updatedReflection = {...reflection, 'answer': e.target.value};
    setReflection(updatedReflection);
    onChange({reflection: JSON.stringify(updatedReflection)});
  }

  return (
    <div id="div_id_reflection" className="form-group">
      <label htmlFor="id_reflection" className="col-form-label">{reflectionPrompts[reflection.promptIndex]} (<a href="#" onClick={cyclePrompt} >Give me another question</a>)</label>
      <div>
        <textarea name="reflection_answer" rows="3" className="textarea form-control" id="id_reflection" value={reflection.answer} onChange={handleChange}/>
      </div> 
    </div>
  );

}

const MeetingFeedback = props => {
  const {formData, updateForm} = props;

  return (
    <form>
      <RatingInput value={formData['rating']} onChange={updateForm}/>
      <AttendanceInput value={formData.attendance} onChange={updateForm}/>
      <ReflectionInput value={formData.reflection} onChange={updateForm} />
    </form>
  )
}

const DelayedPostForm = props => {
  const {actionUrl} = props;

  const [formData, setFormData] = useState({
    rating: props.rating,
    attendance: props.attendance,
    reflection: props.reflection,
  });
  const [pendingChanges, setPendingChanges] = useState(false);
  const [isPosting, setIsPosting] = useState(false);

  const postData = (_formData) => {
    setIsPosting(true);
    // NOTE seems like using state here referst to old state :(
    // Stale closure :(
    const data = new FormData();
    for (const [key, val] of Object.entries(_formData)) {
      if (val){
        data.append(key, val);
      }
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
  };

  let timer = useRef();

  const updateForm = (data, delay=3000) => {
    setFormData({...formData, ...data});
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => postData({...formData, ...data}), delay);
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

export default DelayedPostForm;

