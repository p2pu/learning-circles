import React from 'react'

const NextButton = (props) => (
  <button className="p2pu-btn blue next-tab" onClick={props.onClick}>
    Next<i className="fa fa-arrow-right" aria-hidden="true"></i>
  </button>
)

const BackButton = (props) => (
  <button className="p2pu-btn blue prev-tab" onClick={props.onClick}>
    <i className="fa fa-arrow-left" aria-hidden="true"></i>Back
  </button>
)

const PublishButton = (props) => (
  <button className="p2pu-btn orange publish" onClick={props.onClick}>
    <span style={{ opacity: Number(props.isPublishing), position: "absolute", top: '-4px', left: 'calc(50% - 10px)' }}><div className="btn-loader white" /></span>
    <span style={{ opacity: Number(!props.isPublishing) }}>Publish</span>
  </button>
)

const SaveButton = (props) => (
  <button className="p2pu-btn yellow save" onClick={props.onClick}>
    <span style={{ opacity: Number(props.isSaving), position: "absolute", top: '-4px', left: 'calc(50% - 10px)' }}><div className="btn-loader white" /></span>
    <span style={{ opacity: Number(!props.isSaving) }}>{props.text}</span>
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
    if (!props.learningCircle.draft) {
      return (
        <div className='action-bar'>
          <BackButton onClick={prevTab} />
          <CancelButton onClick={props.onCancel} />
          <SaveButton onClick={() => props.onSubmitForm()} text={'Save'} isSaving={props.isSaving} />
        </div>
      )
    }

    return (
      <div className='action-bar'>
        <BackButton onClick={prevTab} />
        <CancelButton onClick={props.onCancel} />
        <SaveButton onClick={() => props.onSubmitForm()} text={'Save & publish later'} isSaving={props.isSaving} />
        <PublishButton onClick={() => props.onSubmitForm(false)} isPublishing={props.isPublishing} />
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
