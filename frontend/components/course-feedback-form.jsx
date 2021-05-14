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

  const postData = (delay=3000) => {
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => {
      setIsPosting(true);
      const data = new FormData();
      data.append('course_rating', rating);
      data.append('course_rating_reason', ratingReason)
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
        //TODO this.props.showAlert("There was an error sending the validation email. Please contact us at thepeople@p2pu.org.", "warning")
        console.log(err);
      })
    }, delay);
  }

  const updateRating = value => {
    setRating(value);
    postData(1000);
  }

  const ratingChoices = [1,2,3,4,5];

  return (
    <form acion="">
      <p>How well did the online course work as a learning circle?</p>
      <div className="star-rating-input">
        {ratingChoices.map( ratingValue => 
          <label key={ratingValue}>
            <input type="radio" name="goal_rating" value={ratingValue} onClick={ve => updateRating(ratingValue)} />
            <img className={!rating||ratingValue>rating?'dull':''} src={starUrl} />
            <div className="text-center">{ratingValue}</div>
          </label>
        )}
      </div>
      <div className="form-group">
        <label>Why did you give the course {rating} stars</label>
        <input className="form-control" type="text" name="goal_rating_reason" value={ratingReason} onChange={e => { setRatingReason(e.target.value); postData();}} />
      </div>
      { rating && pendingChanges && !isPosting && <><span> pending updates</span></> }
      { isPosting && <><div className="spinner-border spinner-border-sm" role="status"><span className="sr-only">saving...</span></div><span> saving changes</span></> }
      { rating && !pendingChanges && "changes saved" }
    </form>
  );
};

export default CourseFeedbackForm;
