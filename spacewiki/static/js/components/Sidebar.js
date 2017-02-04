import React, { Component } from 'react';
import WelcomeBox from './WelcomeBox';
import Navtree from './Navtree';
import Softlinks from './Softlinks';
import SidebarAttachments from './SidebarAttachments';
import { Revision } from '../API';

export default class Sidebar extends Component {
  render() {
    var welcome ;
    if (this.props.showWelcomeBox) {
      welcome = (
        <WelcomeBox />
      );
    }
    return (
      <div className="small-3 columns sidebar">
        {welcome}
        <Navtree
          currentSlug={this.props.revision.page.slug}
          navigation={this.props.revision.page.navigation} />
        <h2>Related pages</h2>
        <Softlinks
          softlinks={this.props.revision.page.softlinks} />
        <h2>Attachments</h2>
        <SidebarAttachments
          attachments={this.props.revision.page.attachments} />
      </div>
    );
  }
}

Sidebar.propTypes = {
  revision: React.PropTypes.instanceOf(Revision).isRequired
}
