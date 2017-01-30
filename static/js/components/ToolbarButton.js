import React, { Component } from 'react';
import { Link } from 'react-router';

export default class ToolbarButton extends Component {
  render() {
    return (
      <li>
        <Link to={this.props.target} className="small tool-button" href="#">
          <i className={"fa fa-"+this.props.icon}></i> {this.props.label}
        </Link>
      </li>
    );
  }
}

ToolbarButton.propTypes = {
  icon: React.PropTypes.string.isRequired,
  label: React.PropTypes.string.isRequired,
  target: React.PropTypes.string.isRequired
};
ToolbarButton.defaultProps = {
  icon: "",
  label: ""
};
