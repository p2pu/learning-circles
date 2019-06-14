import React from 'react'
import Card from './Card'

class Notification extends React.Component {
  state = { dismissed: false }

  render() {
    return (
      <Card className={`notification ${this.props.level} ${this.state.dismissed ? "dismissed" : ''}`}>
        <div className="d-flex justify-content-between align-items-start">
          <div className="mr-4">
            { this.props.children }
          </div>
          {
            this.props.dismissable &&
            <button type="button" className="close" onClick={() => { this.setState({ dismissed: true })}} aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          }
        </div>
      </Card>
    );
  }
}

export default Notification
