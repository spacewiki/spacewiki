import React, { Component } from 'react';
import { Identity } from '../API';

export default class TitlebarLinks extends Component {
  render() {
    if (this.props.identity) {
      return (
        <ul className="left page-tools">
          <li><a href="#"><i className="fa fa-user"></i> Hello, {this.props.identity.display}</a></li>
        </ul>
      );
    } else {
      return (
        <ul className="left page-tools">
        </ul>
      );
    }
  }
};

TitlebarLinks.propTypes = {
  identity: React.PropTypes.instanceOf(Identity)
};

TitlebarLinks.defaultProps = {
  identity: new Identity()
}
