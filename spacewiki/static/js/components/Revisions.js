import React, { Component } from 'react';

export default class Revisions extends Component {
  constructor(props) {
    super(props);

    var revMap = this.buildRevisionMap(props.revisions);
    this.state = {
      revisionsToIdx: revMap,
      idx: revMap[props.defaultRevision] || -1
    };
  }

  componentWillReceiveProps(nextProps) {
    var idxMap = this.buildRevisionMap(nextProps.revisions);
    var update = {
      revisionsToIdx: idxMap
    };
    if (this.props.defaultRevision != nextProps.defaultRevision || this.state.idx == -1) {
      update.idx = idxMap[nextProps.defaultRevision];
    }
    this.setState(update);
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.idx != this.state.idx) {
      this.props.onRevisionChanged(this.currentRevision);
    }
  }

  buildRevisionMap(revisions) {
    var revisionsToIdx = {}
    for(var i = 0; i < revisions.length; i++) {
      revisionsToIdx[revisions[i].id] = i;
    }
    return revisionsToIdx;
  }

  next() {
    this.advance(1);
  }

  prev() {
    this.advance(-1);
  }

  advance(count) {
    this.setState((prevState, props) => {
      return {
        idx: Math.max(0, Math.min(props.revisions.length-1, prevState.idx+count))
      };
    });
  }

  get currentRevision() {
    return this.props.revisions[this.state.idx] || {
      id: 0
    };
  }

  render() {
    // TODO: Re-add nym textfield
    console.log('render', this.state.idx, this.props.defaultRevision);
    return (
      <div className="welcome-box radius">
        <h2>History</h2>
        <ul className="pagination">
          <li className="arrow"><a href="#" onClick={this.prev.bind(this)}>&laquo;</a></li>
          <li className="current">Revision {this.currentRevision.id}</li>
          <li className="arrow"><a href="#" onClick={this.next.bind(this)}>&raquo;</a></li>
        </ul>
        <form method="post" action={this.props.slug+'/revert'}>
          <input type="hidden" name="revision" value={this.currentRevision.id} />
          <label>Commit message: <input type="text" name="message" /></label>
          <button type="submit">Revert to this revision</button>
        </form>
      </div>
    );
  }
};

Revisions.defaultProps = {
  onRevisionChanged: function() {},
  defaultRevision: 0,
  revisions: []
}
