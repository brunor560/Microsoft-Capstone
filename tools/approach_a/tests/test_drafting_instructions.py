"""Offline prompt contracts and fictional responses through the unchanged parser.

These fixtures demonstrate representable findings, not model accuracy or real
vendor capabilities. No endpoint, credentials, fetching or assessment writes.
"""
import json
import unittest

from tools.approach_a import azure, drafting, store as st


class DraftingInstructions(unittest.TestCase):
    def setUp(self):
        self.catalog = st.Store().catalog()
        self.profile = {
            'id': 'fictional-cli-free-windows', 'tool': 'Fictional CLI', 'surface': 'cli',
            'surface_label': 'Fictional terminal', 'account_and_tier': 'Free', 'platforms': ['Windows'],
            'modes': ['interactive'], 'version': {'value': '2.0'},
            'included_components': ['Native MCP connectivity'], 'exclusions': ['TicketBridge MCP server']}

    def parse(self, fid, status, quote, **overrides):
        response = {
            'feature_id': fid, 'status': status, 'evidence_basis': 'documented_support', 'gap_reason': None,
            'supported_scope': 'Fixture documented capability', 'unsupported_scope': [], 'unestablished_scope': [],
            'required_setup': 'None documented', 'activation_state': 'default',
            'control_mechanism': 'not established', 'constraints': [],
            'evidence': [{'page': 'fixture-reference', 'section': 'CLI scope', 'quote': quote,
                          'claim': 'Fictional capability and scoped requirements'}]}
        response.update(overrides)
        excerpts = [{'page': 'fixture-reference', 'section': 'CLI scope',
                     'text': '\n'.join(e['quote'] for e in response['evidence'])}]
        brief, problems = drafting.check_brief(json.dumps(response), fid, self.catalog, excerpts)
        self.assertEqual(problems, [])
        self.assertIsNotNone(brief)
        self.assertEqual(brief, response)  # Existing fields retain scope/setup distinctions.
        return brief

    def test_instructions_distinguish_delivery_mechanisms_and_scoped_absence(self):
        instructions = drafting.SYSTEM
        builtin = instructions.split('- "Built in":', 1)[1].split('- "Configuration or extension required":', 1)[0]
        self.assertIn('optional setting remains Built in', builtin)
        self.assertIn('required_setup', builtin)
        self.assertIn('activation_state separately', builtin)
        dependency = instructions.split('- "Configuration or extension required":', 1)[1].split('- "Custom implementation required":', 1)[0]
        self.assertIn('required integration', dependency)
        self.assertIn('included, excluded or not established', dependency)
        self.assertIn('Native support for', dependency)
        custom = instructions.split('- "Custom implementation required":', 1)[1].split('- "Unavailable":', 1)[0]
        self.assertIn('code the user must write or maintain', custom)
        self.assertIn('do not invent an owner', custom)
        absent = instructions.split('- "Unavailable":', 1)[1].split('- "Not established from documentation":', 1)[0]
        self.assertIn('within the assessed profile', absent)
        self.assertIn('Silence, excluded dependencies and documentation for another tier do not establish unavailability', absent)

    def test_prompt_requires_claim_support_partial_coverage_and_human_gates(self):
        for requirement in ('both capability claims and material dependency/scope claims',
                            'supported_scope', 'unsupported_scope', 'unestablished_scope',
                            'Quotes are re-verified against cited sections', 'human verification',
                            'independent review by a different team member', 'Do not run or test tools'):
            self.assertIn(requirement, drafting.SYSTEM)
        self.assertIn('Fictional contrasts for classification only (never evidence', drafting.SYSTEM)
        for contrast in ('sandbox=true', 'TicketBridge', 'Free/Windows applicability as unknown'):
            self.assertIn(contrast, drafting.SYSTEM)

    def test_messages_supply_exact_scope_and_membership_without_changing_schema(self):
        feature = next(f for f in self.catalog['features'] if f['id'] == 'F14')
        content = drafting.messages(feature, self.profile, [])[-1]['content']
        for boundary in ('surface key cli', 'Free', 'Windows', 'interactive', '2.0',
                         'Included components: Native MCP connectivity', 'Exclusions: TicketBridge MCP server'):
            self.assertIn(boundary, content)
        self.assertEqual(azure.load_config()['prompt_version'], 'brief-prompt/3')

    def test_native_optional_setting_response_remains_builtin(self):
        brief = self.parse('F08', 'Built in',
            'Alder CLI version 2 provides native isolation when users enable the optional sandbox=true setting.',
            supported_scope='Native execution isolation', required_setup='Enable sandbox=true', activation_state='optional')
        self.assertEqual(brief['activation_state'], 'optional')
        self.assertEqual(brief['status'], 'Built in')

    def test_native_mcp_mechanism_and_excluded_server_workflow_are_distinct(self):
        mechanism = 'Birch CLI version 2 includes native MCP connectivity for Free accounts on Windows in interactive mode.'
        dependency = 'Birch issue tracker workflows require the external TicketBridge MCP server to retrieve and update tickets.'
        native = self.parse('F14', 'Built in', mechanism,
            supported_scope='Native MCP connection mechanism', required_setup='Configure a server connection to use the mechanism',
            activation_state='optional', unestablished_scope=['Server-specific ticket workflows are not established by connectivity alone'])
        workflow = self.parse('F15', 'Configuration or extension required', dependency,
            supported_scope='Documented ticket workflow through TicketBridge, outside the baseline',
            required_setup='TicketBridge MCP server is required and excluded by this profile', activation_state='not established',
            unestablished_scope=['Whether a native ticket workflow exists without TicketBridge'],
            constraints=['Native MCP connectivity does not include TicketBridge or establish a complete CI/CD pipeline'],
            evidence=[{'page': 'fixture-reference', 'section': 'CLI scope', 'quote': mechanism, 'claim': 'Native mechanism'},
                      {'page': 'fixture-reference', 'section': 'CLI scope', 'quote': dependency, 'claim': 'Required workflow dependency'}])
        self.assertEqual(native['status'], 'Built in')
        self.assertEqual(workflow['unsupported_scope'], [])
        self.assertEqual(len(workflow['evidence']), 2)

    def test_documented_user_code_response_identifies_work_and_owner(self):
        self.parse('F03', 'Custom implementation required',
            'For requirement traceability, users must write and maintain the mapping adapter that joins requirements to changes.',
            supported_scope='Traceability through a user-written adapter',
            required_setup='User writes and maintains the requirements-to-changes mapping adapter',
            constraints=['Owner and maintainer: user, as explicitly documented'])

    def test_other_tier_response_keeps_applicability_unknown(self):
        result = self.parse('F16', 'Not established from documentation',
            'Cedar CLI Enterprise provides project audit export with task identifiers and downloadable records of tool calls.',
            evidence_basis='documentation_gap', gap_reason='Audit export is documented for Enterprise; Free and Windows applicability is not established',
            supported_scope='Enterprise audit export is documented; this Free/Windows profile is not established',
            unestablished_scope=['Audit export on Free', 'Audit export on Windows'], required_setup='Not established',
            activation_state='not established')
        self.assertEqual(result['unsupported_scope'], [])

    def test_explicit_scoped_absence_response_is_unavailable(self):
        self.parse('F16', 'Unavailable',
            'Cedar CLI version 2 does not support project audit export on the Free tier under Windows.',
            evidence_basis='documented_absence', supported_scope='None for this explicitly unsupported scoped capability',
            unsupported_scope=['Project audit export on Free under Windows'])

    def test_conflicting_excerpts_preserve_uncertainty_and_both_sources(self):
        yes = 'Alder CLI Free on Windows supports native execution isolation in the interactive mode for version 2.'
        no = 'Alder CLI version 2 release documentation states that execution isolation is unsupported on Windows Free accounts.'
        self.parse('F08', 'Not established from documentation', yes,
            evidence_basis='documentation_conflict', gap_reason='Reference and release documentation conflict on Windows Free isolation in version 2',
            supported_scope='Conflicting documented claims; applicability is unresolved',
            unestablished_scope=['Windows Free isolation in interactive mode, version 2'], activation_state='not established',
            evidence=[{'page': 'fixture-reference', 'section': 'CLI scope', 'quote': yes, 'claim': 'Reference support claim'},
                      {'page': 'fixture-reference', 'section': 'CLI scope', 'quote': no, 'claim': 'Conflicting release claim'}])

    def test_fictional_instruction_examples_cannot_replace_supplied_evidence(self):
        response = {'feature_id': 'F08', 'status': 'Built in', 'evidence_basis': 'documented_support',
                    'activation_state': 'optional', 'control_mechanism': 'not established',
                    'evidence': [{'page': 'Alder fictional example', 'section': 'Example', 'quote': 'sandbox=true'}]}
        brief, problems = drafting.check_brief(json.dumps(response), 'F08', self.catalog, [])
        self.assertIsNone(brief)
        self.assertIn('no usable evidence', problems)
