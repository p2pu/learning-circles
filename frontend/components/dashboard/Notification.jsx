import React from 'react'
import PropTypes from 'prop-types'
import Card from './Card'

class Notification extends React.Component {
  state = { dismissed: this.props.dismissed }

  componentDidUpdate(prevProps) {
    if (prevProps.dismissed !== this.props.dismissed) {
      this.setState({ dismissed: this.props.dismissed })
    }
  }

  render() {
    return (
      <Card className={`notification ${this.props.level} ${this.state.dismissed ? "dismissed" : ''}`}>
        <div className="d-flex justify-content-between align-items-start">
          <div className="mr-4">
            { this.props.children }
          </div>
          {
            this.props.dismissable &&
            <button type="button" className="btn-close" onClick={() => { this.setState({ dismissed: true })}} aria-label="Close"></button>
          }
        </div>
      </Card>
    );
  }
}

Notification.propTypes = {
  dismissed: PropTypes.bool,
  dismissable: PropTypes.bool,
  level: PropTypes.oneOf(['success', 'warning', 'error'])
}

Notification.defaultProps = {
  dismissed: false,
  dismissable: true,
  level: 'success'
}

export default Notification
