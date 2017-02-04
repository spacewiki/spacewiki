import React, { Component } from 'react';

export default class SidebarAttachments  extends Component {
  render() {
    var previews = this.props.attachments.map((attachment) => {
      return (
        <li key={attachment.slug}>
          <a href={attachment.url}>{attachment.slug}</a>
        </li>
      );
    });
    if (previews.length == 0) {
      previews = (
        <li><em>None</em></li>
      );
    }
    return (
      <ul className="attachments">
        {previews}
      </ul>
    );
  }
};

SidebarAttachments.defaultProps = {
  attachments: []
};
