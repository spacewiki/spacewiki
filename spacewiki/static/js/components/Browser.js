import React, { Component } from 'react';
import API, { Page, Revision, PageNotFound, WikiError } from '../API';
import { Route, IndexRoute } from 'react-router';
import Header from './Header';
import WelcomeBox from './WelcomeBox';
import Sidebar from './Sidebar';
import GhostViewer from './GhostViewer';
import ErrorPage from './ErrorPage';

import { browserHistory } from 'react-router';

export default class Browser extends Component {
  constructor(props) {
    super(props);

    this.state = {currentRevision: undefined, missingIndex: false};

    var api = new API();
    api.pageSavedHandler((page) => {
      this.setState({currentRevision: page.latestRevision, error: null});
    });
  }

  componentDidMount() {
    this.fetchPage(this.props.params.splat);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.params.splat != this.props.params.splat) {
      this.fetchPage(nextProps.params.splat || "");
    }
  }

  fetchPage(slug, revision) {
    (new API()).getPage(slug, revision)
      .then((page) => {
        this.setState({currentRevision: page.latestRevision, error: null});
        if (this.state.missingIndex && slug == '') {
          this.setState({missingIndex: false});
        }
      })
      .catch((error) => {
        console.log(typeof(error));
        if (error instanceof PageNotFound && this.props.params.splat == "" && !this.state.missingIndex) {
          this.setState({missingIndex: true});
          browserHistory.push('/docs');
        } else if (error instanceof PageNotFound) {
          this.setState({currentRevision: new Page(false, slug).latestRevision});
          if (slug == '') {
            browserHistory.push('/edit');
          } else {
            browserHistory.push('/'+[slug, 'edit'].join('/'));
          }
        } else if (error instanceof WikiError) {
          console.error("Page load Error: " + error.stack);
          this.setState({error: error});
        } else {
          throw error;
        }
      });
  }

  render() {
    // TODO: Re-add the "welcome to spacewiki!" box
    if (this.state.currentRevision) {
      return (
        <div>
          <Header
            revision={this.state.currentRevision} />
          <main className="row">
            <div className="small-12 columns content">
              <div className="row">
                <Sidebar
                  revision={this.state.currentRevision}
                  showWelcomeBox={this.state.missingIndex} />
                <div className="small-9 columns">
                  {React.cloneElement(this.props.children, {revision: this.state.currentRevision})}
                </div>
              </div>
            </div>
          </main>
        </div>
      );
    } else if (this.state.error) {
      return (<ErrorPage message={this.state.error.message}/>);
    } else {
      return (<GhostViewer />);
    }
  }
}
