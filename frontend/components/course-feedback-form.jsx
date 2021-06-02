import React, {useState, useRef} from 'react'

import DelayedPostForm from './manage/delayed-post-form';

const Form = props => {
  const {formData, updateForm} = props;
  return (
    <form>
      <p>How well did the online course work as a learning circle?</p>
      <div className="star-rating-input">
        {[1,2,3,4,5].map( ratingValue => 
          <label key={ratingValue}>
            <input 
              type="radio" 
              name="course_rating"
              value={ratingValue} 
              onClick={
                ve => updateForm({course_rating: ratingValue})
              }
            />
            <img className={!formData.course_rating||ratingValue>formData.course_rating?'dull':''} src={props.starUrl} />
            <div className="text-center">{ratingValue}</div>
          </label>
        )}
      </div>
      <div className="form-group">
        <label>Why did you give the course {formData.course_rating} stars?</label>
        <textarea name="course_rating_reason" rows="3" className="textarea form-control" value={formData.course_rating_reason} onChange={e => updateForm({course_rating_reason: e.target.value})} />
      </div>
    </form>
  );
}

const CourseFeedbackForm = props => {
  const {actionUrl} = props;
  let [completionState, setCompletionState] = useState(props.completionState);

  let initialFormData = {
    course_rating: props.courseRating,
    course_rating_reason: props.courseRatingReason?props.courseRatingReason:'',
  };

  if (completionState == 'pending'){
    return (
      <div className="meeting-item pending" >
        <p>Share your thoughts about the course</p>
      </div>
    );
  }

  return (
    <div className={"meeting-item " + completionState} >
      <p>Share your thoughts about the course</p>
      <div className="meeting-item-details">
        <DelayedPostForm
          createObject={false}
          actionUrl={actionUrl}
          initialValues={initialFormData}
          onFormSubmitted={ () => setCompletionState('done')}
        >
          <Form {...props} />
        </DelayedPostForm>
        <p>What recommendations do you have for other facilitators who are using “{props.course_title}"? Consider sharing additional resources you found helpful, activities that worked particularly well, or any agendas or facilitator guides you created.</p>
        <p><a className="p2pu-btn btn-primary" href={props.courseDiscourseUrl} >Share course feedback</a></p>
      </div>
    </div>
  );
};

export default CourseFeedbackForm;
