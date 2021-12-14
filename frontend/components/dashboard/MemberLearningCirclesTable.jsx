import React, { Component } from "react";
import moment from "moment";
import axios from 'axios';
import { sortBy } from 'lodash';


export default class LearningCirclesTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      learningCircles: [],
      count: 0,
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = (params={}) => {
    const url = '/api/drf/member_learningcircles/';
    axios({url, method: 'GET', responseType: 'json'}).then(res => {
      console.log(res);
      if (res.data.errors) {
      }
      this.setState({ learningCircles: res.data.results, count: res.data.count})
    }).catch(err => {
      console.log(err)
    });
  }


  render() {
    const orderedLearningCircles = sortBy(this.state.learningCircles, lc => lc.next_meeting_date || lc.start_date)

    if (this.state.learningCircles.length === 0) {
      return(
        <div className="py-2">
          <div>No upcoming learning circles.</div>
        </div>
      )
    }

    return (
      <div className="learning-circles-table">
        <div className="table-responsive d-none d-md-block">
          <table className="table">
            <thead>
              <tr>
                <td>Learning circle</td>
                <td>Next meeting</td>
                <td></td>
              </tr>
            </thead>
            <tbody>
              {
                orderedLearningCircles.map(lc => {
                  let date = moment(lc.next_meeting_date).format('MMM D, YYYY')

                  return(
                    <tr key={ lc.id }>
                      <td>{ lc.name }</td>
                      <td>{ date }</td>
                      { !!lc.user_signup && 
                        <td style={{textAlign: 'center'}}><strong>Signed up</strong></td>
                      }
                      { !lc.user_signup && 
                        <td style={{textAlign: 'center'}}><a href={ lc.signup_url } className="p2pu-btn btn btn-sm dark">signup</a></td>
                      }
                    </tr>
                  )
                })
              }
            </tbody>
          </table>
        </div>

        <div className="d-md-none">
          {
            this.state.learningCircles.map(lc => {
              const date = lc.next_meeting_date ? moment(lc.next_meeting_date).format('MMM D, YYYY') : "n/a";
              return(
                <div className={`meeting-card p-2`} key={lc.id}>
                  <p className="bold">{lc.name}</p>

                  <div className="d-flex">
                    <div className="pr-2">
                      <div className="bold">Next Meeting</div>
                    </div>

                    <div className="flex-grow px-2">
                      <div className="">{ date }</div>
                    </div>
                  </div>
                  { !!lc.user_signup && 
                    <p><strong>Signed up</strong></p>
                  }
                  { !lc.user_signup && 
                    <a href={ lc.signup_url } className="p2pu-btn btn btn-sm dark m-0 my-2">signup</a> 
                  }
                </div>
              )
            })
          }
        </div>
      </div>
    );
  }
}
