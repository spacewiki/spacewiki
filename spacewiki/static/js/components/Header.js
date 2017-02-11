import React, { Component } from 'react';

import TitlebarLinks from './TitlebarLinks';
import Toolbar from './Toolbar';
import ProgressLine from './ProgressLine';
import API from '../API';
import { Revision, Identity } from '../Model';

import { Link } from 'react-router';

export default class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      apiProgress: 0
    };
    var api = new API();
    api.progressHandler((p) => {
      this.setState({apiProgress: p});
    });
  }

  render() {
    return (
      <div className="sticky">
        <header data-topbar className="top-bar">
          <ul className="title-area">
            <li className="name">
              <Link to="/">
                <h1>SpaceWiki</h1>
              </Link>
            </li>
          </ul>
        <section className="top-bar-section">
          <TitlebarLinks identity={this.props.currentUser} />
        </section>
        </header>
        <Toolbar 
          revision={this.props.revision} />
        <ProgressLine progress={this.state.apiProgress} />
      </div>
    );
  }
};

Header.propTypes = {
  revision: React.PropTypes.instanceOf(Revision).isRequired,
  currentUser: React.PropTypes.instanceOf(Identity)
};

Header.defaultProps = {
  currentUser: new Identity()
}
