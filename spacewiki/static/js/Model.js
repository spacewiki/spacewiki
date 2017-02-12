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
    this.softlinks = this.data.softlinks || [];
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
