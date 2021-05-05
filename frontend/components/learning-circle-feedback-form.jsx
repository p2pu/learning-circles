import React, {useState} from 'react'
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const LearningCircleFeedbackForm = props => {
  const {starUrl, actionUrl} = props;

  const [goalRating, setGoalRating] = useState(props.facilitatorGoalRating);

  const postValue = value => {
    setGoalRating(value);
    const data = new FormData();
    data.append('facilitator_goal_rating', value);
    axios.post(actionUrl, data).then(res => {
      if (res.status === 200) {
        //TODO this.props.showAlert("We've sent you a validation email, check your inbox!", "success")
        console.log('updated facilitator goal rating');
      } else {
        // TODO
        console.log("error saving rating");
      }
    }).catch(err => {
      //TODO this.props.showAlert("There was an error sending the validation email. Please contact us at thepeople@p2pu.org.", "warning")
      console.log(err);
    })

  }

  return (
    <form acion="">
      <label>
        <input type="radio" name="facilitator_goal_rating" value="1" onClick={e => postValue(1)} />
        <img className={!goalRating||1>goalRating?'dull':''} src={starUrl} />
        <div className="text-center">1<br/>not at all</div>
      </label>
      <label>
        <input type="radio" name="facilitator_goal_rating" value="2" onClick={e => postValue(2)} />
        <img className={!goalRating||2>goalRating?'dull':''} src={starUrl} />
        <div className="text-center">2</div>
      </label>
      <label>
        <input type="radio" name="facilitator_goal_rating" value="3" onClick={e => postValue(3)} />
        <img className={!goalRating||3>goalRating?'dull':''} src={starUrl} />
        <div className="text-center">3<br/>somewhat</div>
      </label>
      <label>
        <input type="radio" name="facilitator_goal_rating" value="4" onClick={e => postValue(4)} />
        <img className={!goalRating||4>goalRating?'dull':''} src={starUrl} />
        <div className="text-center">4</div>
      </label>
      <label>
        <input type="radio" name="facilitator_goal_rating" value="5" onClick={e => postValue(5)} />
        <img className={!goalRating||5>goalRating?'dull':''} src={starUrl} />
        <div className="text-center">5<br/>completely</div>
      </label>
    </form>
  );
};

export default LearningCircleFeedbackForm;
