import React from 'react'

const CardBody = (props) => {
  return (
    <div className="card-body">
      {props.children}
    </div>
  );
}

export default CardBody
