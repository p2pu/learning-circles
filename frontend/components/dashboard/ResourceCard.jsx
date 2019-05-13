import React, { Component } from 'react'
import ReactDOM from 'react-dom'
import { DISCOURSE_API_URL, FACILITATOR_RESOURCE_TYPES } from '../../helpers/constants';

const ResourceCard = props => {

  const { topic, defaultImagePath, ...rest } = props;
  const url = `${DISCOURSE_API_URL}/t/${topic.slug}`;
  const resourceType = topic.tags.find(tag => FACILITATOR_RESOURCE_TYPES.includes(tag));

  const getImageUrl = () => {
    if (topic.image_url) {
      return topic.image_url;
    };

    if ((!!topic.featured_link) && (topic.featured_link_root_domain === "youtube.com")) {
      const videoId = topic.featured_link.split('?v=')[1];
      return `https://img.youtube.com/vi/${videoId}/hq2.jpg`;
    };

    return defaultImagePath;
  };

  const imgUrl = getImageUrl();

  return (
      <div className="resource-card col-md-4 col-sm-12 col-12" onClick={() => window.location.href = url} {...rest}>
        <div className="image">
          { imgUrl && <img src={imgUrl} /> }
          <div className="overlay">
            {resourceType && <div className="topic-type minicaps">{resourceType}</div>}
          </div>
        </div>
        <div className="title"><a href={url}>{topic.title}</a></div>
      </div>
  );
}

export default ResourceCard
