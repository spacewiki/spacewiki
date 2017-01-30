import React, { Component } from 'react';
import { Link } from 'react-router';

export default class WelcomeBox extends Component {
  render() {
    return (
      <div className="welcome-box radius">
        <h2>Welcome to SpaceWiki!</h2>
        <p>You have not yet created this wiki's index
        page, and are viewing  the included documentation.
        <Link to="/edit">Create your index page</Link> to get started.</p>
      </div>
    );
  }
}
