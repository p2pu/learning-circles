import React, { useState } from 'react'

const RatingInput = props => {
  const {value, onChange} = props;

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
              onChange={e => onChange({"rating": e.target.value})}
              checked={value==option[0]?true:null}
            />
            <img src={option[2]} />
            <div className="text-center">{option[1]}</div>
          </label>
        )}
      </div>
    </div>
  );
}

export default RatingInput;
