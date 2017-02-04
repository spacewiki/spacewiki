import React, { Component } from 'react';

export default class ProgressLine extends Component {
  render() {
    return (
      <div className="progress-line">
        <div className="progress-fill" style={{width: this.props.progress+"%"}}>
        </div>
      </div>
    );
  }
}

ProgressLine.defaultProps = {
  progress: 100
};
