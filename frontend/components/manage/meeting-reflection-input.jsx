import React, { useState } from 'react'

const MeetingReflectionInput = ({value, onChange}) => {
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

export default MeetingReflectionInput;

