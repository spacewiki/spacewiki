import React, { Component } from 'react';

export default class GhostBox extends Component {
  render() {
    var contents;
    if (this.props.src) {
      contents = React.createElement(this.props.component, {ghosted: this.props.src});
    } else {
      contents = this.props.placeholder
    }
    return (
      <span className={this.props.src ? "" : "ghost-box"}>{contents}</span>
    )
  }
}

GhostBox.propTypes = {
  placeholder: React.PropTypes.string
}
