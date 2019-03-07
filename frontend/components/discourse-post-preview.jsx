import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';


const DiscoursePostPreview = ({ post }) => {
  const dateString = new Date(post.created_at).toLocaleDateString("en-US", { year: 'numeric', month: 'short', day: 'numeric' })
  const regex = new RegExp('^<p>(.*?)<\/p>', 'gm')
  const truncatedPost = regex.exec(post.cooked)[0]

  return (
    <div className="post my-3 mb-4">
      <div className="post-author my-2"><strong>{ post.name }</strong> posted on <strong>{ dateString }</strong>:</div>
      <div className="post-text" dangerouslySetInnerHTML={{ __html: truncatedPost }}></div>
    </div>
  )
}


DiscoursePostPreview.propTypes = {
    id: PropTypes.number,
    name: PropTypes.string,
    created_at: PropTypes.string,
    cooked: PropTypes.string,
}

export default DiscoursePostPreview