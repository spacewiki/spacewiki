# Hosted SpaceWiki

All wiki-as-a-service software sucks. SpaceWiki.io sucks less than most.

SpaceWiki is provided as a service via https://spacewiki.io/. There, users can
sign in with their slack teams and each team is provisioned a wiki. Payment is
optional but requested.

## Development

You'll need the following tools available:

* virtualenv
* ngrok (optional; only for slack button testing)
* A slack API key: https://api.slack.com/apps/
* A stripe API key: https://stripe.com/
* Postgres

To begin:

  $ virtualenv virtualenv/
  $ source virtualenv/bin/activate
  $ pip install -r requirements.txt

Next, configure local_hosted_settings.py with appropriate values:

* ``SLACK_KEY`` - Public slack key from api.slack.com
* ``SLACK_SECRET`` - Private slack API key from api.slack.com
* ``SPACE_DB_URL_PATTERN`` - This must be a string containing '%s' which will be
  replaced with the team's database name. For example,
  ``postgres://postgres:postgres@localhost/%s`` for the default docker postgres
  container
* ``ADMIN_DB_URL`` - A peewee database URI
* ``STRIPE_SECRET_KEY`` - Secret API key from stripe.com
* ``STRIPE_KEY`` - Public API key from stripe.com
* ``SECRET_SESSION_KEY`` - Used to generate session cookies. Keep this secret,
  as it is used to process slack logins between subdomains.

To start the server:

  $ ./hosted-manage.py runserver

If you plan on interacting with the slack workflows at all, you'll need to
expose your local server somewhere internet reachable. NGrok is a fantastic free
tool for this. Once started, you'll be given a domain such as
https://d13163fbc.ngrok.io/. In your slack app's OAuth & Permissions page, add
this URL to the list of redirect URLs.

## Deployment

Deployment is done by pushing to spacewiki.io:/srv/spacewiki/git. Server-side
hooks will rebuild and reload the application.
