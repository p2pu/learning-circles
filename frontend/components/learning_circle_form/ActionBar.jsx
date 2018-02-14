import React from 'react'

const NextButton = (props) => (
  <button className="p2pu-btn blue" onClick={props.onClick}>
    Next<i className="fa fa-arrow-right" aria-hidden="true"></i>
  </button>
)

const BackButton = (props) => (
  <button className="p2pu-btn blue" onClick={props.onClick}>
    <i className="fa fa-arrow-left" aria-hidden="true"></i>Back
  </button>
)

const PublishButton = (props) => (
  <button className="p2pu-btn orange publish" onClick={props.onClick}>
    Publish
  </button>
)

const SaveButton = (props) => (
  <button className="p2pu-btn yellow save" onClick={props.onClick}>
    Save & publish later
  </button>
)

const CancelButton = (props) => (
  <button onClick={props.onClick} className="p2pu-btn transparent">Cancel</button>
)

const ActionBar = (props) => {
  const nextTab = () => {
    props.changeTab(props.currentTab + 1)
  }

  const prevTab = () => {
    props.changeTab(props.currentTab - 1)
  }

  if (props.currentTab === 4) {
    return (
      <div className='action-bar'>
        <BackButton onClick={prevTab} />
        <CancelButton onClick={props.onCancel} />
        <SaveButton onClick={props.onSubmitForm} />
        <PublishButton onClick={() => props.updateFormData({ published: true}, props.onSubmitForm)} />
      </div>
    )
  }

  if (props.currentTab === 0) {
    return (
      <div className='action-bar'>
        <CancelButton onClick={props.onCancel} />
        <NextButton onClick={nextTab} />
      </div>
    )
  }

  return (
    <div className='action-bar'>
      <BackButton onClick={prevTab} />
      <CancelButton onClick={props.onCancel} />
      <NextButton onClick={nextTab} />
    </div>
  );
}

export default ActionBar;
