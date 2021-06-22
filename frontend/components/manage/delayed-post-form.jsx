import React, { useState, useRef } from 'react'
import axios from 'axios'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const DelayedPostForm = props => {
  const {actionUrl} = props;

  const [formData, setFormData] = useState({...props.initialValues});
  const [pendingChanges, setPendingChanges] = useState(false);
  const [isPosting, setIsPosting] = useState(false);

  const postData = (_formData) => {
    setIsPosting(true);
    axios(actionUrl, {method: props.createObject?'POST':'PUT', data: _formData}).then(res => {
      setIsPosting(false)
      if (res.status === 201) {
        setPendingChanges(false);
        props.onFormSubmitted();
        props.onObjectCreated(res.data);
        console.log('created object');
      } else if (res.status === 200){
        setPendingChanges(false);
        props.onFormSubmitted(res.data);
      } else {
        // TODO
        console.log("error saving course rating");
      }
    }).catch(err => {
      setIsPosting(false)
      //TODO 
      console.log(err);
    })
  };

  let timer = useRef();
  const updateForm = (update, delay=3000) => {
    setFormData({...formData, ...update});
    setPendingChanges(true);
    if (timer.current) {
      clearTimeout(timer.current);
    }
    timer.current = setTimeout(() => postData({...formData, ...update}), delay);
  }

  let children = React.Children.map(props.children, child => 
    React.cloneElement(child, {formData, updateForm, pendingChanges, isPosting})
  );

  return (
    <>
      {children}
      <div className="text-muted">
        { pendingChanges && !isPosting && <span> pending updates</span> }
        { isPosting && <><div className="spinner-border spinner-border-sm" role="status"><span className="sr-only">saving...</span></div><span> saving changes</span></> }
        { !pendingChanges && "changes saved" }
      </div>
    </>
  );
}

export default DelayedPostForm;
