import React, { Component } from 'react';
import { Link } from 'react-router';

export default class Softlinks extends Component {
  render() {
    var links = this.props.softlinks.map((softlink) => {
      return (
        <li key={softlink.slug}>
          <Link to={softlink.slug}>{softlink.title}</Link>
        </li>
      );
    });
    return (
      <ul className="softlinks">
        {links}
      </ul>
    );
  }
};

Softlinks.defaultProps = {
  softlinks: []
};
