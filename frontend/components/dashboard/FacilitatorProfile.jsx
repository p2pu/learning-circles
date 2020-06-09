import React, { Fragment } from 'react'

import "../stylesheets/facilitator-profile.scss"

const FacilitatorProfile = ({ facilitator, themeColor }) => {
  return (
    <div className="pos-relative card-outer">
      <div className="pos-relative card-upper">
        <div className="circle-bg" />
        { facilitator.avatarUrl ?
          <img className="img-fluid card-img" src={facilitator.avatarUrl } alt="Facilitator image" /> :
          <img className="img-fluid card-img" src={`/static/images/avatars/p2pu_avatar_blue.png`} />
        }
      </div>

      <div className="card card-lower">
        <div className="profile-info text-center">
          <h4 className="mb-3 mt-4">{ `${facilitator.firstName} ${facilitator.lastName}` }</h4>
          { facilitator.bio && <p className="text-left">{ facilitator.bio }</p> }
        </div>

        <div className="grid-wrapper">
          {
            facilitator.teamName &&
            <Fragment>
              <div className="label">Team</div>
              <div>{ facilitator.teamName }</div>
            </Fragment>
          }
          {
            facilitator.city &&
            <Fragment>
              <div className="label">City</div>
              <div>{ facilitator.city }</div>
            </Fragment>
          }
        </div>
        <div className="card-actions text-right">
          <a href="/en/accounts/settings/">Edit your profile</a>
        </div>
      </div>
    </div>
  );
}

export default FacilitatorProfile
