import React, { Component } from 'react';
import { Link } from 'react-router';

class Navlink extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Link to={this.props.url}>{this.props.title}</Link>
    );
  }
}

export default class Navtree extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    var subpages = this.props.navigation.subpages.map((subpage) => {
      return (
        <li key={subpage.slug}>
          <Navlink url={subpage.slug} title={subpage.title}/>
        </li>
      );
    });

    var siblings = this.props.navigation.siblings.map((sibling) => {
      var subnav;
      var activeClass;
      if (sibling.slug == '/'+this.props.currentSlug) {
        subnav = subpages;
        activeClass = "current";
      }
      return (
        <li key={sibling.slug}>
          <span className={activeClass}>
            <Navlink url={sibling.slug} title={sibling.title} />
          </span>
          <ul className="navtree">
            {subnav}
          </ul>
        </li>
      );
    });


    var localTree = (
      <ul className="navtree">
        {siblings}
      </ul>
    );

    var ret = localTree;
    for(var parent of this.props.navigation.parents) {
      ret = (
        <ul className="navtree">
          <li>
            <Navlink url={parent.slug} title={parent.title} />
            {ret}
          </li>
        </ul>
      );
    }
    return ret;
  }
};

Navtree.defaultProps = {
  navigation: {
    siblings: [],
    subpages: [],
    parents: []
  },
  currentSlug: "",
};
