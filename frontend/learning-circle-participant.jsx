import React from 'react';
import ReactDOM from 'react-dom';

import ParticipantDash from './components/participant-dash';

const reactDataEl = document.getElementById('react-data');
const reactData = JSON.parse(reactDataEl.textContent);


const element = document.getElementById('learning-circle-timeline');
ReactDOM.render(<ParticipantDash {...reactData} />, element);
