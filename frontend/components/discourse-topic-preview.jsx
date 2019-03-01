import React from 'react'
import PropTypes from 'prop-types';

export default class DiscourseTopicPreview extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return(
            <p>Discussion goes here!</p>
        )
    }
}


DiscourseTopicPreview.propTypes = {
    thread: PropTypes.string,
}
