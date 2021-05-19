import React, {useState, useRef} from 'react'
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const LearningCircleFeedbackForm = props => {
  const {starUrl, actionUrl} = props;

  const [goalRating, setGoalRating] = useState(props.facilitatorGoalRating);

  const [pendingChanges, setPendingChanges] = useState(false);
  const [isPosting, setIsPosting] = useState(false);

  let timer = useRef();

  const postValue = (value, delay=3000) => {
    setGoalRating(value);
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => {
      setIsPosting(true);
      const data = new FormData();
      data.append('facilitator_goal_rating', value);
      axios.post(actionUrl, data).then(res => {
        setIsPosting(false)
        if (res.status === 200) {
          setPendingChanges(false);
          //TODO
          console.log('updated facilitator goal rating');
        } else {
          // TODO
          console.log("error saving rating");
        }
      }).catch(err => {
        setIsPosting(false)
        //TODO
        console.log(err);
      });
    }, delay);
  }

  return (
    <form acion="">
      <div className="star-rating-input">
        {[[1,'not at all'],[2],[3,'somewhat'],[4],[5, 'completely']].map(value =>
          <label key={value[0]}>
            <input type="radio" name="facilitator_goal_rating" value={value[0]} onClick={e => postValue(value[0])} />
            <img className={!goalRating||value[0]>goalRating?'dull':''} src={starUrl} />
            <div className="text-center">{value[0]}{value.length == 2 && <><br />{value[1]}</> } </div>
          </label>
        )}
      </div>
      <div className="text-muted">
        { goalRating && pendingChanges && !isPosting && <span> pending updates</span> }
        { isPosting && <><div className="spinner-border spinner-border-sm" role="status"><span className="sr-only">saving...</span></div><span> saving changes</span></> }
        { goalRating && !pendingChanges && "changes saved" }
      </div>
    </form>
  );
};

export default LearningCircleFeedbackForm;
