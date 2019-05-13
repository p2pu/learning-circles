import React from 'react';
import axios from "axios";
import { API_ENDPOINTS } from "../../helpers/constants";


export default class DashboardTitle extends React.Component {

  constructor(props){
    super(props);
    this.state = {};
  }

  componentDidMount() {
    const url = API_ENDPOINTS["whoami"];

    axios.get(url).then(res => {
      if (res.data.user && res.data.user !== "anonymous") {
        this.setState({ user: res.data.user })
      }
    })
  }

  render() {
    const title = this.state.user ? `${this.state.user}'s Learning Circle Dashboard` : `Learning Circle Dashboard`;

    return (
      <header className="text-center my-5">
        <h1>{ title }</h1>
      </header>
    );
  }
}
