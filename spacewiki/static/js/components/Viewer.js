import React, { Component } from 'react';
import { Revision } from '../Model';
import Raw from './Raw';

export default class Viewer extends Component {
  render() {
    return (
      <Raw html={this.props.revision.rendered} />
    );
  }
};

Viewer.propTypes = {
  revision: React.PropTypes.instanceOf(Revision).isRequired
}

Viewer.defaultProps = {
  revision: new Revision()
}
