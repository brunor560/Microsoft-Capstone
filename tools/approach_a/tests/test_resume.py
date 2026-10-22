"""Interrupt and resume (offline, using a synthetic brief and a cached page)."""
import json
import os
import unittest
from unittest import mock

from tools.approach_a import cmd_people, model, sources, store as st, ui
from tools.approach_a.__main__ import parser
from tools.approach_a.tests.test_validation import Base

PAGE = ('<html><head><title>Fixture CLI - Fixture Tool | Docs</title></head><body><main>'
        '<h1>Fixture</h1><h2>Permissions</h2><p>Deny rules block the action immediately.</p>'
        '</main></body></html>')


class Resume(Base):
    def setUp(self):
        super().setUp()
        url = 'https://docs.example.invalid/permissions/'
        cand_dir = self.store.path('candidates', 'fixture')
        os.makedirs(os.path.join(cand_dir, 'briefs', 'cli'))
        cand = {'tool_key': 'fixture', 'tool': 'Fixture Tool', 'default_surface': 'cli',
                'docs': {'base_url': 'https://docs.example.invalid/', 'publisher': 'Fixture',
                         'allowed_prefixes': ['https://docs.example.invalid/'], 'surface_labels': {'Fixture CLI': 'cli'}},
                'surfaces': {'cli': {'seed_pages': ['permissions', 'permissions']}}}
        json.dump(cand, open(os.path.join(cand_dir, 'candidate.json'), 'w'))
        for fid in ('F07', 'F10'):
            json.dump({'feature_id': fid, 'status': 'Built in', 'supported_scope': 'Deny rules',
                       'evidence': [{'page': 'permissions', 'section': 'Permissions',
                                     'quote': 'Deny rules block the action immediately'}]},
                      open(os.path.join(cand_dir, 'briefs', 'cli', fid + '.json'), 'w'))
        from tools.approach_a import fetch, pages
        fetch.PageCache(self.store).put(sources.page_key(url), pages.to_text(PAGE), PAGE)
        p = self.add_profile()
        m = self.store.load('manifest.json')
        m['profiles'][0]['tool_key'] = 'fixture'
        self.store.save('manifest.json', m)

    def args(self, *extra):
        return parser().parse_args(['resume', '--offline', '--operator', 'ross'] + list(extra))

    def test_interrupt_then_resume(self):
        calls = {'n': 0}
        real = ui.progress

        def boom(phase, n, total, msg):
            if phase == 'assess':
                calls['n'] += 1
                if calls['n'] == 9:
                    raise KeyboardInterrupt
            real(phase, n, total, msg)

        with mock.patch.object(ui, 'progress', boom), self.assertRaises(KeyboardInterrupt):
            cmd_people.resume(self.store, self.args())
        log = [e['event'] for e in self.store.worklog()]
        self.assertIn('research_started', log)
        self.assertIn('research_stopped', log)
        self.assertNotIn('validated', log)
        # The cell completed before the interrupt (F07) is kept; nothing was challenged or validated.
        states = model.counts(self.store.load('cells.json')['cells'])
        self.assertEqual(states['drafted'], 1)
        self.assertEqual(states['challenged'], 0)
        # Resume detects the interrupted run and completes it.
        cmd_people.resume(self.store, self.args())
        states = model.counts(self.store.load('cells.json')['cells'])
        self.assertEqual(states['challenged'], 2)
        self.assertEqual(states['pending'], 16)
        log = [e['event'] for e in self.store.worklog()]
        self.assertIn('validated', log)


if __name__ == '__main__':
    unittest.main()
