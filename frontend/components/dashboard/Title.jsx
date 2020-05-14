import React from 'react';

const DashboardTitle = ({ user, userData }) => {
  if (user) {
    return (
      <header className="text-center my-5">
        <h1>{`Hello ${userData.firstName} 👋`}</h1>
        <p>Welcome to your learning circle dashboard</p>
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
