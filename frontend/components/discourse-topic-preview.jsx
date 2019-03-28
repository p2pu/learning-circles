import React from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

import DiscoursePostPreview from "./discourse-post-preview"

const defaultPost = {
  id: 123,
  name: "Learning Circles Bot",
  created_at: new Date(),
  cooked: "<p>Have you used this course in a learning circle? Please leave your review for other facilitators! What did you like or not like about it? If you have any questions about the course, feel free to ask.</p>",
}


export default class DiscourseTopicPreview extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      posts: [
        {
          id: 123,
          name: "Learning Circles Bot",
          created_at: new Date(),
          cooked: this.props.discourseText,
        }
      ]
    }
  }

    componentDidMount() {
      console.log(this.props.topicUrl)
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
