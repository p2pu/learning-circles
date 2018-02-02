import React from 'react'


const Alert = (props) => {
  if (props.show) {
    return (
      <div className='alert-container'>
        <div className={`alert alert-dismissible alert-${props.type}`} role="alert">
          <div className='alert-content'>
            { props.children }
          </div>
          <button type="button" className="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        </div>
      </div>
    );
  }

  return <div></div>
}


export default Alert;