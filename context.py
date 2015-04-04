import git
import settings
import os
import model

def init(app):
    @app.context_processor
    def add_git_version():
        repo = git.Repo(os.path.dirname(os.path.realpath(__file__)))
        return dict(git_version=repo.head.commit.hexsha)

    @app.context_processor
    def add_random_page():
        page = None
        try:
            page = model.Page.select().order_by(peewee.fn.Random()).limit(1)[0]
        except:
            pass
        return dict(random_page=page)

    @app.context_processor
    def add_site_settings():
        return dict(settings=settings)
