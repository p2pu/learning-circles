import React from "react";

const ResourceCard = ({imgUrl, title, url}) => 
  <div className="col-12 col-md d-flex flex-row flex-md-column resource-card mt-3 mt-md-4 text-md-center">
    <img className="me-3 me-md-0" src={imgUrl}/>
    <div className="title">{title}</div>
    <a href={url} target="_blank"></a>
  </div>;


const RecommendedResources = props => {
  return (
    <div className="row resources">
      <ResourceCard
        title="Getting started"
        imgUrl="/static/images/icons/getting-started.svg"
        url="https://docs.p2pu.org/methodology/learning-circle-checklist"
      />
      <ResourceCard
        title="Using the tools"
        imgUrl="/static/images/icons/tool-docs.svg"
        url="https://docs.p2pu.org/tools-and-resources/tools-for-learning-circles"
      />
      <ResourceCard
        title="Help"
        imgUrl="/static/images/icons/support.svg"
        url="https://www.p2pu.org/en/help/"
      />
      { 
        props.isMemberTeam && 
        <>
          <ResourceCard
            title="Meet with Q"
            imgUrl="/static/images/icons/team-support.svg"
            url={props.memberSupportUrl}
          />
          <ResourceCard
            title="Teams documentation"
            imgUrl="/static/images/icons/team-docs.svg"
            url="https://docs.p2pu.org/teams/about-teams"
          />
        </> 
      }
    </div>
  );
}

export default RecommendedResources
