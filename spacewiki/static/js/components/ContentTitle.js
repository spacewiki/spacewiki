import React, { Component } from 'react';
import { Identity } from '../API';

export default class ContentTitle extends Component {
  render() {
    return (
      <div>
        <h1>
          {this.props.title}
        </h1>
        <div className="last-edited">
          <p>Last modified {this.props.lastModified} by {this.props.author.display}</p>
          <p className="edit-message">{this.props.message}</p>
        </div>
      </div>
    );
  }
}

ContentTitle.propTypes = {
  title: React.PropTypes.string,
  message: React.PropTypes.string,
  lastModified: React.PropTypes.string,
  author: React.PropTypes.instanceOf(Identity)
}

ContentTitle.defaultProps = {
  title: "",
  message: "",
  lastModified: "",
  author: new Identity()
};
