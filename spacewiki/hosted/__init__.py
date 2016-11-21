"""Code that runs spacewiki.io"""
import dispatcher, app

application = dispatcher.SubdomainDispatcher('spacewiki.io', dispatcher.make_wiki_app, app.create_app)
