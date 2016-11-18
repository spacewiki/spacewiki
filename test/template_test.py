from spacewiki import model, wikiformat
from spacewiki.wikiformat import directives
import unittest
from spacewiki.app import APP as app
from playhouse.test_utils import test_database
from peewee import SqliteDatabase

test_db = SqliteDatabase(':memory:')

class ParserTestCase(unittest.TestCase):
    def test_directives(self):
        self.assertEqual(directives.render("", ''), "")
        self.assertEqual(directives.render("{{foo}}", ''), "{{[[foo]]}}")

    def test_full_empty_render(self):
        self.assertEqual(wikiformat.render_wikitext("", ''), "")

    def test_recursive_templates(self):
        with test_database(test_db, [model.Page, model.Revision]):
            page = model.Page.create(title='recursive', slug='recursive')
            page.newRevision('{{recursive}}', '', '')
            canary = "{{Max include depth of"
            self.assertTrue(canary in directives.render("{{recursive}}", ''))
