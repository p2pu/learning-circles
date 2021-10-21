import React, {useState} from 'react'

import DelayedPostForm from './manage/delayed-post-form';
import Star from './manage/star';

const FacilitatorGoalRatingInput = ({value, onChange, facilitatorGoal}) => {
  const options = [
    [1,'not at all'],
    [2],
    [3,'somewhat'],
    [4],
    [5, 'completely']
  ];

  if (!facilitatorGoal){
    return '';
  }

  return (
    <div>
      <p>When you signed up, we asked what you hoped to achieve by facilitating a learning circle, and you wrote <strong>"{facilitatorGoal}"</strong>.</p>
      <p>To what extent did you achieve this?</p>

      <div className="star-rating-input">
        { options.map(optionValue => 
          <label key={optionValue[0]}>
            <input 
              type="radio"
              name="facilitator_goal_rating"
              value={optionValue[0]}
              onClick={ e => onChange({facilitator_goal_rating: optionValue[0]}) } 
            />
            <Star selected={ value && optionValue[0] <= value } />
            <div className="text-center">
              {optionValue[0]}
              {optionValue.length == 2 && <br /> } 
              {optionValue.length == 2 && optionValue[1]} 
            </div>
          </label>
        )}
      </div>
    </div>
  );
}

const CourseRatingInput = ({value, onChange, courseTitle}) => {
  return (
    <div className="form-group">
      <p>How well did the course "{courseTitle}" work in a learning circle?</p>
      <div className="star-rating-input">
        {[1,2,3,4,5].map( ratingValue => 
          <label key={ratingValue}>
            <input 
              type="radio" 
              name="course_rating"
              value={ratingValue} 
              onClick={() => onChange({course_rating: ratingValue})}
            />
            <Star selected={ value && ratingValue <= value } />
            <div className="text-center">{ratingValue}</div>
          </label>
        )}
      </div>
    </div>
  );
};


const CourseRatingReasonInput = ({value, formData, onChange}) => (
  <div className="form-group">
    <label>Why did you give the course {formData.course_rating} stars?</label>
    <textarea name="course_rating_reason" rows="3" className="textarea form-control" value={value} onChange={e => onChange({course_rating_reason: e.target.value})} />
  </div>
);


const SurveyPrompt = props => {
  if (props.surveyCompleted){
    return <p>Thank you for completing the survey</p>
  }
  return <>
    <p>Can we ask you a few more questions? It will only take 5 minutes.</p>
    <p><a className="p2pu-btn btn-primary" href={props.surveyUrl} target="_blank">Complete the facilitator survey</a></p>
    </>;
}


const LearningCircleFeedbackForm = props => {
  const {formData, updateForm} = props;
  return (
    <form>
      <FacilitatorGoalRatingInput
        value={formData.facilitator_goal_rating} 
        onChange={updateForm}
        facilitatorGoal={props.facilitatorGoal}
      />
      <CourseRatingInput 
        value={formData.course_rating} 
        onChange={updateForm}
        courseTitle={props.courseTitle}
      />
      <CourseRatingReasonInput 
        value={formData.course_rating_reason} 
        onChange={updateForm}
        formData={formData}
      />
    </form>
  );
}

const LearningCircleFeedback = props => {
  const {actionUrl} = props;
  let [completionState, setCompletionState] = useState(props.completionState);

  let initialFormValues = {
    facilitator_goal_rating: props.facilitatorGoalRating,
    course_rating: props.courseRating,
    course_rating_reason: props.courseRatingReason?props.courseRatingReason:'',
  }

  if (completionState == 'pending'){
    return (
      <div className="meeting-item pending" >
        <p>Reflect on your experience</p>
      </div>
    );
  }

  let checkCompletion = (updatedData) => {
    if ( props.surveyCompleted || updatedData.facilitator_goal_rating && updatedData.course_rating && updatedData.course_rating_reason) {
      setCompletionState("done");
    } else {
      setCompletionState("todo");
    }
  }

  return (
    <div className={"meeting-item " + completionState}>
      <p>Reflect on your experience</p>
      <div className="meeting-item-details">
        <DelayedPostForm
          createObject={false}
          actionUrl={actionUrl}
          initialValues={initialFormValues}
          onFormSubmitted={ updatedData => checkCompletion(updatedData) }
        >
          <LearningCircleFeedbackForm {...props} />
        </DelayedPostForm>
        <SurveyPrompt {...props} />
      </div>
    </div>
  );
};

export default LearningCircleFeedback;
