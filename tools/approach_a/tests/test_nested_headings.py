import unittest
from tools.approach_a import pages


class NestedHeadings(unittest.TestCase):
    def test_vendor_anchor_markup_keeps_heading_and_quote_in_its_section(self):
        source = '<main><h1>Desktop</h1><h2><div><a><svg>icon</svg></a></div><span>Choose permissions</span></h2><p>Require approval before execution.</p><h2>Next</h2><p>Other text</p></main>'
        text = pages.to_text(source)
        self.assertIn('## Choose permissions\n', text)
        self.assertEqual(pages.locate(text, 'Desktop > Choose permissions',
                                     'Require approval before execution.', {}, [])['status'], 'verified')
        self.assertEqual(pages.locate(text, 'Next', 'Require approval before execution.', {}, [])['status'],
                         'quote_outside_section')

    def test_multiline_and_escaped_heading_text(self):
        text = pages.to_text('<main><h2><div></div><span>Tools &amp;\n permissions</span></h2><p>Claim</p></main>')
        self.assertEqual(pages.sections(text)[0]['title'], 'Tools & permissions')
