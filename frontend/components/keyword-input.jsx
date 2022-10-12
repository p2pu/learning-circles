import React, { Component } from 'react'
import CreatableSelect from 'react-select/creatable';

/*
 * Input for selecting multiple keywords as a comma seperated string 
 */

export default class KeywordInput extends Component {
  constructor(props){
    super(props);
    let keywords = [];
    if (props.value){
      keywords = props.value.split(',').map(e => { return {label: e, value: e};});
    }
    this.state = {keywords: keywords}
    this.handleSelect = this.handleSelect.bind(this);
  }

  handleSelect(selected){
    this.setState({ keywords: selected });
  }

  render(props) {
    const keywordOptions = Array.from(this.props.keywords);
    keywordOptions.sort();

    return(
      <span>
        <input type="hidden" value={this.state.keywords.map(t=>t.value).join(',')} name="keywords" />
        <CreatableSelect
          name="keywords_input"
          isMulti={true}
          value={this.state.keywords}
          onChange={this.handleSelect}
          options={keywordOptions.map(keyword => {
            return {
              value: keyword,
              label: keyword,
            };
          })}
        />
      </span>
    )
  }
}
