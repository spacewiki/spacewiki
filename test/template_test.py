import model
import wikiformat
import unittest


class ParserTestCase(unittest.TestCase):
    def test_wikitemplates(self):
        self.assertEqual(wikiformat.wikitemplates("", ''), "")
        self.assertEqual(wikiformat.wikitemplates("{{foo}}", ''), "{{[[foo]]}}")

    def test_recursive_templates(self):
        try:
            page = model.Page.create(title='recursive', slug='recursive')
        except:
            page = model.Page.get(slug='recursive')
        page.newRevision('{{recursive}}', '')
        self.assertEqual(wikiformat.wikitemplates("{{recursive}}", ''), "{{Max include depth of 11 reached before [[recursive]]}}")
