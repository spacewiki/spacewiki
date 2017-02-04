let instance = null;

import ExtendableError from 'es6-error';

export class WikiError extends ExtendableError {
  constructor(response) {
    super(response.statusText);
    this.response = response;
  }
}

export class PageNotFound extends WikiError {}

export default class API {
  constructor() {
    if (!instance) {
      instance = this;
    }

    this.progress = () => {};
    this.saved = () => {};

    return instance;
  }

  progressHandler(cb) {
    this.progress = cb;
  }

  pageSavedHandler(cb) {
    this.saved = cb;
  }

  getPage(slug, revision) {
    var url = '/' + slug;
    if (revision) {
      url += '@'+revision;
    }
    this.progress(25);
    return fetch(url, {credentials: 'include'}).then((response) => {
      this.progress(75);
      if (response.ok) {
        return response.json();
      } else {
        if (response.status == 404) {
          throw new PageNotFound(response);
        } else {
          throw new WikiError(response);
        }
      }
    }).then((data) => {
      this.progress(100);
      return new Page(data);
    }).catch((error) => {
      this.progress(100);
      throw error;
    });
  }

  savePage(slug, pageData) {
    this.progress(25);
    var form = new FormData();
    form.set('slug', pageData.slug);
    form.set('title', pageData.title);
    form.set('body', pageData.body);
    form.set('message', pageData.message);
    return fetch('/' + slug, {credentials: 'include', method: "POST", body: form}).then((response) => {
      this.progress(75);
      if (response.ok) {
        return response.json();
      } else {
        throw new WikiError('Save error: '+response.statusText);
      }
    }).then((data) => {
      var p = new Page(data);
      this.saved(p);
      this.progress(100);
      return p;
    }).catch((error) => {
      this.progress(100);
      throw error;
    });
  }
}

export class Page {
  constructor(pageJSON, slug) {
    if (pageJSON) {
      this.data = pageJSON;
    } else {
      this.data = {
        latest: {
          timestamp: "Today",
          author: {
            display: "Anonymous"
          }
        }
      }
    }

    this.latestRevision = new Revision(this.data.latest || {}, this);
    this.navigation = this.data.navigation || {subpages: [], parents: [], siblings: []};
    this.slug = this.data.slug || slug;
    this.title = this.data.title || this.slug;
    this.url = '/' + this.slug
  }
}

export class Revision {
  constructor(revisionJSON, parentPage) {
    if (revisionJSON) {
      this.data = revisionJSON;
    } else {
      this.data = {
        timestamp: "Today",
        author: {
          display: "Anonymous"
        }
      }
    }

    this.body = this.data.body || "";
    this.id = this.data.id || 0;
    this.page = parentPage;
    this.timestamp = this.data.timestamp || "Today";
    this.author = new Identity(this.data.author || {});
    this.rendered = this.data.rendered || "";
  }
}

export class Identity {
  constructor(authorJSON) {
    if (authorJSON) {
      this.data = authorJSON
    } else {
      this.data = {
        display: "Anonymous"
      }
    }

    this.display = this.data.display || "Anonymous";
  }
}
