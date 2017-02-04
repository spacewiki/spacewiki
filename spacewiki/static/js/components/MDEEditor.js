import React, { Component } from 'react';
import SimpleMDE from 'simplemde';

export default class extends Component {
  componentDidMount() {
    this.mde = new SimpleMDE(this.textarea);
    this.mde.codemirror.on("changes", () => {
      this.props.onChange(this.mde.value());
    });
  }

  componentWillReceiveProps(nextProps) {
    if (this.mde && this.mde.value() != nextProps.value) {
      this.mde.value(nextProps.value);
    }
  }

  render() {
    return (
        <textarea
          name={this.props.name}
          ref={(e) => {this.textarea=e;}}
          value={this.props.value}
          onChange={this.props.onChange}
          defaultValue={this.props.defaultValue}></textarea>
    );
  }
};
