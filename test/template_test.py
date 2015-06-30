from spacewiki import model, wikiformat
from spacewiki.wikiformat import directives
import unittest
from spacewiki.app import app

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        app.config['DATABASE'] = 'sqlite:///:memory:'
        with app.app_context():
            model.syncdb()

    def test_directives(self):
        self.assertEqual(directives.render("", ''), "")
        self.assertEqual(directives.render("{{foo}}", ''), "{{[[foo]]}}")

    def test_full_empty_render(self):
        self.assertEqual(wikiformat.render_wikitext("", ''), "")

    def test_recursive_templates(self):
        try:
            page = model.Page.create(title='recursive', slug='recursive')
        except:
            page = model.Page.get(slug='recursive')
        page.newRevision('{{recursive}}', '', '')
        self.assertEqual(directives.render("{{recursive}}", ''),
                         "{{Max include depth of 11 reached before " + \
                             "[[recursive]]}}")
