import React from 'react';

const DashboardTitle = ({ user, userData }) => {
  if (user) {
    return (
      <div className="row pt-3">
        <header className="col-12 col-md-8">
          <h1 style={{ lineHeight: 1, marginBottom: '1rem' }}>{`Hello ${userData.firstName} 👋`}</h1>
          <p style={{ lineHeight: 1, marginBottom: '1rem' }}>Welcome to your learning circle dashboard.</p>
        </header>
        <div className="account-settings col text-md-end">
            <a href="/en/accounts/settings/" className="btn btn-sm p2pu-btn orange secondary">Account settings</a>
        </div>
      </div>
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
