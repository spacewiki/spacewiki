let instance = null;

import 'whatwg-fetch';
import ExtendableError from 'es6-error';
import { Page } from './Model';

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
    this.loggedOut = () => {};

    return instance;
  }

  loggedOutHandler(f) {
    this.loggedOut = f;
  }

  logout() {
    this.progress(25);
    return this.fetch('/_/identity/logout', {credentials: 'include'}).then((response) => {
      this.loggedOut();
      return response;
    });
  }

  fetch(url, options) {
    this.progress(25);
    return fetch(url, options).then((response) => {
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
    }).catch((error) => {
      this.progress(100);
      throw error;
    });
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
    return this.fetch(url, {credentials: 'include'}).then((data) => {
      this.progress(100);
      return new Page(data);
    });
  }

  savePage(slug, pageData) {
    this.progress(25);
    var form = new FormData();
    form.set('slug', pageData.slug);
    form.set('title', pageData.title);
    form.set('body', pageData.body);
    form.set('message', pageData.message);
    return this.fetch('/' + slug, {credentials: 'include', method: "POST", body: form}).then((data) => {
      var p = new Page(data);
      this.saved(p);
      return p;
    });
  }
}
