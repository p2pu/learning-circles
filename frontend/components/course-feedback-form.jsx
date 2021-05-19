import React, {useState, useRef} from 'react'
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const CourseFeedbackForm = props => {
  const {starUrl, actionUrl} = props;

  const [rating, setRating] = useState(props.courseRating);
  const [ratingReason, setRatingReason] = useState(props.courseRatingReason?props.courseRatingReason:'');
  const [pendingChanges, setPendingChanges] = useState(false);
  const [isPosting, setIsPosting] = useState(false);

  let timer = useRef();

  const postData = (formState, delay=3000) => {
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => {
      setIsPosting(true);
      const data = new FormData();
      if (formState.rating){
        data.append('course_rating', formState.rating);
      }
      if (formState.ratingReason){
        data.append('course_rating_reason', formState.ratingReason)
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

  const updateRating = value => {
    setRating(value);
    let formState = { rating: value }
    if (ratingReason) {
      formState.ratingReason = ratingReason;
    }
    postData(formState, 1000);
  }

  const updateRatingReason = value => {
    setRatingReason(value);
    let formState = { ratingReason: value };
    if (rating) {
      formState.rating = rating;
    }
    postData(formState);
  }

  return (
    <form acion="">
      <p>How well did the online course work as a learning circle?</p>
      <div className="star-rating-input">
        {[1,2,3,4,5].map( ratingValue => 
          <label key={ratingValue}>
            <input type="radio" name="goal_rating" value={ratingValue} onClick={ve => updateRating(ratingValue)} />
            <img className={!rating||ratingValue>rating?'dull':''} src={starUrl} />
            <div className="text-center">{ratingValue}</div>
          </label>
        )}
      </div>
      <div className="form-group">
        <label>Why did you give the course {rating} stars</label>
        <textarea name="rating_reason" rows="3" className="textarea form-control" value={ratingReason} onChange={e => updateRatingReason(e.target.value)} />
      </div>
      { rating && pendingChanges && !isPosting && <><span> pending updates</span></> }
      { isPosting && <><div className="spinner-border spinner-border-sm" role="status"><span className="sr-only">saving...</span></div><span> saving changes</span></> }
      { rating && !pendingChanges && "changes saved" }
    </form>
  );
};

export default CourseFeedbackForm;
