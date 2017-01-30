import React, { Component } from 'react';

class GhostTitle extends Component {
  render() {
    return (
      <div className="ghost-title">
        <h1> </h1>
        <div className="last-edited">
          <p> </p>
          <p className="edit-message"></p>
        </div>
      </div>
    )
  }
}

class GhostToolbar extends Component {
  render() {
    return (
      <div data-topbar className="row content-title">
        <div className="button-bar tools">
          <ul className="button-group round">
          </ul>
        </div>
        <GhostTitle />
      </div>
    )
  }
}

class GhostHeader extends Component {
  render() {
    return (
      <div className="sticky">
        <header data-topbar className="top-bar">
          <ul className="title-area">
            <li className="name">
              <a href="/">
                <h1>SpaceWiki</h1>
              </a>
            </li>
          </ul>
          <section className="top-bar-section">
            <ul className="left page-tools">
              <li><a href="#"> </a></li>
            </ul>
          </section>
        </header>
        <GhostToolbar />
      </div>
    )
  }
}

class GhostNav extends Component {
  render() {
    return (
      <div className="small-3 columns">
        <ul className="navtree">
          <li><a href="#"></a>
            <ul className="navtree">
              <li><a href="#"> </a></li>
              <li><a href="#"> </a></li>
              <li><a href="#"> </a></li>
            </ul>
          </li>
          <li><a href="#"> </a></li>
          <li><a href="#"> </a></li>
        </ul>
      </div>
    );
  }
}

export default class GhostViewer extends Component {
  render() {
    return (
      <div className="ghost-viewer">
        <GhostHeader />
        <main className="row">
          <div className="small-12 columns content">
            <div className="row">
              <GhostNav />
              <div className="small-9 columns">
                <div className="ghost-text"></div>
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }
}
