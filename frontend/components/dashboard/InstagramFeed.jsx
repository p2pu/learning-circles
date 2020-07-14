import React, { Component } from "react";
import axios from "axios";
import ApiHelper from "../../helpers/ApiHelper";
import moment from "moment";

const POST_LIMIT = 2;


class EmbeddedPost extends Component {
  constructor(props) {
    super(props);
    this.state = {
      html: "<p>...</p>",
    };
  }

  componentDidMount() {
    const url = `https://api.instagram.com/oembed/?url=${this.props.postUrl}&omitscript=true`
    axios.get(url).then(res => {
      this.setState({ html: res.data.html })
    })
  }

  componentDidUpdate(prevProps) {
    if (window.instgrm) {
      window.instgrm.Embeds.process();
    }
  }

  render() {
    return(
      <div className="my-2 flex-grow">
        <div dangerouslySetInnerHTML={{ __html: this.state.html }} />
      </div>
    )
  }
}

export default class InstagramFeed extends Component {
  constructor(props) {
    super(props);
    this.state = {
      items: [],
      errors: []
    };
  }

  componentDidMount() {
    this.populateResources();
  }

  populateResources = () => {
    const api = new ApiHelper('instagram');

    const onSuccess = (data) => {
      if (data.status && data.status === "error") {
        console.log(data)
        return this.setState({ errors: "There are no recent posts available." })
      }

      this.setState({ items: data.items })
    }

    api.fetchResource({ callback: onSuccess, params: {} })
  }


  render() {
    const latestPosts = this.state.items.slice(0,POST_LIMIT);

    if (this.state.errors.length > 0) {
      return(
        <div className="py-2">
          { this.state.errors }
        </div>
      )
    };

    return (
      <div className="instagram-feed d-flex flex-wrap">
        {
          latestPosts.map(post => {
            return(
              <EmbeddedPost postUrl={post.permalink} key={post.id} />
            )
          })
        }

      </div>
    );
  }
}
