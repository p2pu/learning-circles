import React from 'react'
import Autocomplete from 'react-autocomplete'

export default class CourseInput extends React.Component{
  constructor(props){
    super(props);
    this.state = {
      courseList: [],
      courseId: props.value,
      q: props.q,
    };
    this.fetchCourses = this.fetchCourses.bind(this);
  }

  componentWillMount(){
    this.fetchCourses();
  }

  fetchCourses(query){
    var url = '/api/courses/';
    if (query) {
      url = url + '?q=' + encodeURIComponent(query);
    }
    fetch(url).then(res => res.json()).then( data => {
      this.setState({courseList: data.items});
    });
  }

  render() {
    const {label, hint, error} = this.props;
    let errorSpan = null;
    if (error) {
      errorSpan = (
        <span id="error_1_id_course" className="help-block"><strong>{error}</strong></span> 
      );
    }
    return (
      <div>
        <label htmlFor="id_course" className="control-label">{label}</label>
        <div className="controls" style={{position:'relative'}}> 
          <input 
            id="id_course"
            type="hidden"
            name="course" 
            value={this.state.courseId} 
          />
          <Autocomplete 
            getItemValue={item => item.title}
            items={this.state.courseList}
            inputProps={{className: 'form-control'}}
            wrapperStyle={{}}
            renderItem={(item, isHighlighted) =>
                <div style={{ background: isHighlighted ? 'lightgray' : 'white' }}>
                  {item.title}
                </div>
            }
            value={this.state.q}
            onChange={(e, value) => {
              this.setState({
                q: e.target.value
              });
              this.fetchCourses(e.target.value);
            }}
            onSelect={(val, item) => this.setState({
              courseId: item.id,
              q: item.title,
            })}
          />
          <span 
            id="searchclear" style={{
              position: 'absolute', top: '1em', right: '10px', cursor: 'pointer'
            }}
            className="glyphicon glyphicon-remove-circle"
            onClick={() => {
              this.setState({q: '', courseId: ''});
              this.fetchCourses('');
            }}
          >
          </span>
          {errorSpan}
          <p id="hint_id_course" className="help-block">{hint}</p> 
        </div> 
      </div>
    );
  }
}
