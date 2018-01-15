import React from 'react'
import Search from './form_fields/Search'

export default class CourseSection extends React.Component{
  constructor(props){
    super(props);
    this.state = {};
  }

  render() {
    return (
      <Search />
    );
  }
}
