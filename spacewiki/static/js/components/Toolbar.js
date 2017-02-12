import React, { Component } from 'react';
import $ from 'jquery-browserify';

import ToolbarButton from './ToolbarButton';
import ContentTitle from './ContentTitle';

import { Page, Revision } from '../Model';

export default class Toolbar extends Component {
  componentDidMount() {
    $(document).foundation('topbar', 'reflow');
  }
  render() {
    return (
      <div data-topbar className="row content-title">
        <div className="button-bar tools">
          <ul className="button-group round">
            <ToolbarButton icon="eye" label="View" target={this.props.revision.page.url}  />
            <ToolbarButton icon="pencil" label="Edit" target={this.props.revision.page.url+"/edit"} />
          </ul>
        </div>
        <ContentTitle
          lastModified={this.props.revision.timestamp}
          title={this.props.revision.page.title}
          author={this.props.revision.author}
          message={this.props.revision.message} />
      </div>
    );
  }
};

Toolbar.propTypes = {
  revision: React.PropTypes.instanceOf(Revision).isRequired
};
