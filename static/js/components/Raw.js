import React, { Component } from 'react';

export default class Raw extends Component {
  renderHTML(r) {
    if (r) {
      r.innerHTML = this.props.html;
    }
  }

  render() {
    return (
      <p ref={(div) => {this.renderHTML(div);}} />
    );
  }
};

Raw.defaultProps = {
  html: ''
};
