import React, { Component } from 'react';

import SidebarAttachments from './SidebarAttachments';
import API from '../API';
import { Page, Revision, Identity } from '../Model';
import Browser from './Browser';
import Editor from './Editor';
import Viewer from './Viewer';

import { Router, Route, IndexRoute, browserHistory } from 'react-router'

export default class App extends Component {
  constructor(props) {
    super(props);
    console.log("Booting up with %o", props.initialConfig);
  }

  render() {
    var user = new Identity(this.props.initialConfig.current_user);
    return (
      <Router history={browserHistory}>
        <Route initialUser={user} component={Browser} >
          <Route path="/*/edit" component={Editor} />
          <Route path="/edit" component={Editor} />
          <Route path="*" component={Viewer} />
        </Route>
      </Router>
    );
  }

};

App.propTypes = {
  initialConfig: React.PropTypes.object,
};

App.defaultProps = {
  initialConfig: {}
};
