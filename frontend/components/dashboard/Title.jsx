import React from 'react';

const DashboardTitle = ({ user, userData }) => {
  if (user) {
    return (
      <header className="text-center my-5">
        <h1 style={{ lineHeight: 1, marginBottom: '1rem' }}>{`Hello ${userData.firstName} 👋`}</h1>
        <p style={{ lineHeight: 1, marginBottom: '1rem' }}>Welcome to your learning circle dashboard.</p>
      </header>
    )
  } else {
    return (
      <header className="text-center my-5">
        <h1>Learning Circle Dashboard</h1>
      </header>
    )
  }
}


export default DashboardTitle
