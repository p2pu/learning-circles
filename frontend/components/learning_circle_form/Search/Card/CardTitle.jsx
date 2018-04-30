import React from 'react'

const CardTitle = (props) => {
  return (
    <div className="card-title">
      <h4 className="title">{ props.children }</h4>
    </div>
  );
}

export default CardTitle
