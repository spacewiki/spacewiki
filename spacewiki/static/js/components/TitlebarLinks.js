import $ from 'jquery-browserify';
import React, { Component } from 'react';
import API, { Identity } from '../API';

import { Link } from 'react-router';

class DropdownMenu extends Component {
  componentDidMount() {
    $(document).foundation('dropdown', 'reflow');
  }

  render() {
    return (
      <li className="has-dropdown">
        <a href="#">{this.props.label}</a>
        <ul className="dropdown">
          {this.props.children}
        </ul>
      </li>
    )
  }
}

export default class TitlebarLinks extends Component {
  doLogout(evt) {
    evt.preventDefault();
    var api = new API();
    api.logout();
  }

  constructor(props) {
    super(props);
    this.doLogout = this.doLogout.bind(this);
  }

  render() {
    if (this.props.identity) {
      return (
        <ul className="left page-tools">
          <DropdownMenu label={(<span><i className="fa fa-user"></i> Hello, {this.props.identity.display}</span>)}>
            <li><a href="#" onClick={this.doLogout}><i className="fa fa-door"></i> Logout</a></li>
          </DropdownMenu>
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
