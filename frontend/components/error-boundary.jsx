import React from 'react'
import Promise from 'promise-polyfill'
import 'whatwg-fetch'

function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}

function sendLog(level, message){
  fetch('/log/', {
        method: 'POST',
        mode: 'cors',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        redirect: 'follow',
    body: JSON.stringify({level, message}),
  }).then(t=> console.log(t));
}

window.sendLog = sendLog;

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // You can also log the error to an error reporting service
    let message = {
      error,
      info,
      scope: this.props.scope,
    };
    sendLog('ERROR', message);
    console.log(message);
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return (
        <div>
          <h1>Something unexcpeted happened.</h1>
        </div>
      );
    }

    return this.props.children; 
  }
}
