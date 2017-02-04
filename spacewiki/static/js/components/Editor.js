import React, { Component } from 'react';
import DropdownEdit from './DropdownEdit';
import MDEEditor from './MDEEditor';
import Attachments from './Attachments';
import API, { Page, Revision } from '../API';
import { browserHistory } from 'react-router';

export default class Editor extends Component {
  constructor(props) {
    super(props);
    this.state = {
      message: "",
      slug: props.revision.page.slug,
      title: props.revision.page.title,
      body: props.revision.body
    }

    this.save = this.save.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    this.setState({
      slug: nextProps.revision.page.slug,
      title: nextProps.revision.page.title,
      body: nextProps.revision.body
    });
  }

  save(evt) {
    evt.preventDefault();
    var api = new API();
    var pageData = {
      slug: this.state.slug,
      title: this.state.title,
      body: this.state.body,
      message: this.state.message
    }
    api.savePage(this.props.revision.page.slug, pageData).then((page) => {
      console.log(page);
      browserHistory.push('/'+page.slug);
    });
  }

  render() {
    return (
      <form onSubmit={this.save}>
        <div className="editor-row">
          <div className="content active">
            <dl className="sub-nav">
              <DropdownEdit
                name="title"
                label="Title"
                help="Fix any spelling or capitalization errors here before saving."
                originalValue={this.props.revision.page.title}
                value={this.state.title}
                onChange={(e) => this.setState({title: e.target.value})} />
              <DropdownEdit
                name="slug"
                value={this.state.slug}
                originalValue={this.props.revision.page.slug}
                label="Slug"
                help="Change the URL before saving."
                onChange={(e) => this.setState({slug: e.target.value})}/>
            </dl>
            <MDEEditor name="body"
              value={this.state.body}
              onChange={(e) => this.setState({body: e})} />
          </div>
        </div>
        <div className="row">
          <div className="small-12 columns">
            <Attachments attachments={this.props.revision.page.attachments}/>
          </div>
        </div>
        <div className="row">
          <div className="large-12 columns">
            <label>
              Commit message:
              <input
                type="text"
                name="message"
                onChange={(e) => {this.setState({message: e.target.value})}} />
            </label>
            <button type="submit">Save</button>
          </div>
        </div>
      </form>
    )
  }
};

Editor.propTypes = {
  revision: React.PropTypes.instanceOf(Revision),
  onPageSaved: React.PropTypes.func
};

Editor.defaultProps = {
  onPageSaved: () => {},
  revision: new Page().latestRevision
};
