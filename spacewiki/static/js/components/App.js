import React, { Component } from 'react';

import SidebarAttachments from './SidebarAttachments';
import API, { Page, Revision } from '../API';
import Browser from './Browser';
import Editor from './Editor';
import Viewer from './Viewer';

import { Router, Route, IndexRoute, browserHistory } from 'react-router'

export default class App extends Component {
  constructor(props) {
    super(props);
    console.log("Booting up with %o", props.initialConfig);
  }

  componentWillUpdate(nextProps, nextState) {
    if (nextState.currentSlug != this.state.currentSlug) {
      this.fetchPage(nextState.currentSlug, nextProps.revision);
    }
  }

  render() {
    return (
      <Router history={browserHistory}>
        <Route component={Browser}>
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
