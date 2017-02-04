import $ from 'jquery-browserify';
import React, { Component } from 'react';

export default class DropdownEdit extends Component {
  componentDidMount() {
    $(document).foundation('dropdown', 'reflow');
  }

  render() {
    var changedClass = this.props.value != this.props.originalValue ? 'active' : '';
    changedClass += " editor-button";
    return (
      <span>
        <dt>{this.props.label}:</dt>
        <dd><a className={changedClass} data-dropdown={"dropdown-"+this.props.name}><i className="fa fa-pencil"></i>{this.props.value}</a></dd>
        <div id={"dropdown-"+this.props.name} data-dropdown-content className="f-dropdown content">
        <em>{this.props.help}</em>
        <p>Currently: {this.props.originalValue}</p>
        <input
          type="text"
          onChange={this.props.onChange}
          value={this.props.value}
          defaultValue={this.props.defaultValue}
          name={this.props.name} />
        </div>
      </span>
    );
  }
}

DropdownEdit.defaultProps = {
  label: "",
  help: "",
  name: ""
};
