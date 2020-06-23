import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

import DiscoursePostPreview from "./discourse-post-preview"

export default class DiscourseTopicPreview extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      posts: []
    }
  }

  componentDidMount() {
    if (this.props.topicUrl && (this.props.topicUrl !== "None")) {
      const url = `${this.props.topicUrl}/last.json`
      axios.get(url)
        .then(res => {
          if (res.data.post_stream) {
            const posts = res.data.post_stream.posts.slice(-3)
            this.setState({ posts })
          }
        })
        .catch(err => {
          console.log(err)
        })
    }
  }

  render() {
    return(
      <div className="discourse-preview">
        {
          this.state.posts.map(post => <DiscoursePostPreview key={`post-${post.id}`} post={post} />)
        }
      </div>
    )
  }
}


DiscourseTopicPreview.propTypes = {
  topicUrl: PropTypes.string,
}
