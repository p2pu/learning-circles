import React, {useState, useRef} from 'react'

import DelayedPostForm from './manage/delayed-post-form';


const SurveyPrompt = props => {
  if (props.surveyCompleted){
    return <p>Thank you for completing the survey</p>
  }
  return <>
    <p>Can we ask you a few more questions? It will only take 5 minutes.</p>
    <p><a className="p2pu-btn btn-primary" href={props.surveyUrl}>Complete the facilitator survey</a></p>
  </>;
}

const GoalRatingForm = props => {
  const {formData, updateForm} = props;
  const options = [
    [1,'not at all'],
    [2],
    [3,'somewhat'],
    [4],
    [5, 'completely']
  ];

  return (
    <form>
      <p>When you signed up, we asked what you hoped to achieve by facilitating a learning circle, and you wrote <strong>"{props.facilitatorGoal}"</strong>.</p>
      <p>To what extent did you achieve this?</p>

      <div className="star-rating-input">
        { options.map(value => 
          <label key={value[0]}>
            <input 
              type="radio"
              name="facilitator_goal_rating"
              value={value[0]}
              onClick={ e => updateForm({facilitator_goal_rating: value[0]}) } 
            />
            <img className={!formData.facilitator_goal_rating||value[0]>formData.facilitator_goal_rating?'dull':''} src={props.starUrl} />
            <div className="text-center">
              {value[0]}
              {value.length == 2 && <br /> } 
              {value.length == 2 && value[1]} 
            </div>
          </label>
        )}
      </div>
    </form>
  );
}

const LearningCircleFeedbackForm = props => {
  const {actionUrl} = props;
  let [completionState, setCompletionState] = useState(props.completionState);

  let initialFormValues = {
    facilitator_goal_rating: props.facilitatorGoalRating,
  }

  return (
    <div className={"meeting-item " + completionState}>
      <p>Reflect on your experience</p>
      <div className="meeting-item-details">
        { props.facilitatorGoal && 
            <div>
              <DelayedPostForm
                createObject={false}
                actionUrl={actionUrl}
                initialValues={initialFormValues}
                onFormSubmitted={ () => setCompletionState('done')}
              >
                <GoalRatingForm {...props} />
              </DelayedPostForm>
            </div>
        }
        <SurveyPrompt {...props} />
      </div>
    </div>
  );
};

export default LearningCircleFeedbackForm;
