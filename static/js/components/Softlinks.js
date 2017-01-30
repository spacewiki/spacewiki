import React, { Component } from 'react';

export default class Softlinks extends Component {
  render() {
    var links = this.props.softlinks.map((softlink) => {
      return (
        <li key={softlink.slug}>
          <a href={softlink.slug}>{softlink.title}</a>
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
