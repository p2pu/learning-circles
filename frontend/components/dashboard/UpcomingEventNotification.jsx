import React from 'react'
import axios from 'axios'

import Notification from './Notification'

const UpcomingEventNotification = ({ event }) => {
  const datetime = new Date(event.datetime)
  const date = datetime.toLocaleString('default', { day: 'numeric', month: 'short', year: 'numeric' });
  const time = datetime.toLocaleString('default', { hour: 'numeric', minute: '2-digit' });
  return (
    <Notification level="success" dismissable={true}>
      <p className="mb-0">There's an upcoming event that you might be interested in!</p>
      <p className="mb-0"><strong>{event.title}</strong>{` is taking place on ${date} at ${time}.`}</p>
      <a href={event.link}>Go to the event page</a>
    </Notification>
  );
}

export default UpcomingEventNotification
