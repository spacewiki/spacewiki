import React, { Component } from 'react';

export default class Attachments extends Component {
  constructor(props) {
    super(props);
    this.state = {attachments: props.attachments || []};
  }

  componentWillReceiveProps(nextProps) {
    this.setState({attachments: nextProps.attachments || []});
  }

  render() {
    var previews = this.state.attachments.map((attachment) => {
      var templateText = "{{attachment:"+attachment.slug+"}}";
      return (<li key={attachment.slug}>
        <img src={attachment.url} />
        <input type="text" readOnly value={templateText} />
      </li>);
    });
    return (<ul className="attachment-list">{previews}</ul>);
  }
}

