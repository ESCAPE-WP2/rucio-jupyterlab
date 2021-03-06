"""
Possible states:
- Attachments cache: empty, exists
- File replica cache: empty, some exists, all exists
- DID states: All available, not all available
- Force fetch: no, yes

Case 1: Attachments exist, all replica cache exists, all available, no force fetch -> should not fetch
Case 2: Attachments exist, all replica cache exists, not all available, no force fetch -> should fetch rule status only
Case 3: Attachments exist, some replica cache exists, all available, no force fetch -> should fetch replicas only
Case 4: Attachments exist, some replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 5: Attachments exist, no replica cache exists, all available, no force fetch -> should fetch replicas only
Case 6: Attachments exist, no replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 7: Attachments not exist, no replica cache exists, all available, no force fetch -> should fetch replicas only
Case 8: Attachments not exist, no replica cache exists, not all available, no force fetch -> should fetch replicas and rule status
Case 9: Force fetch, all available -> should fetch replicas only
Case 10: Force fetch, not all available -> should fetch replicas and rule status
"""

import json
from unittest.mock import call
from rucio_jupyterlab.handlers.did_details import DIDDetailsHandler
from rucio_jupyterlab.mode_handlers.replica import ReplicaModeHandler
from rucio_jupyterlab.rucio import RucioAPIFactory
from .mocks.mock_handler import MockHandler

def test_get_handler(mocker, rucio):
    mock_self = MockHandler()
    mock_active_instance = 'atlas'

    def mock_get_query_argument(key, default=None):
        args = {
            'namespace': mock_active_instance,
            'poll': '0',
            'did': 'scope:name'
        }
        return args.get(key, default)

    mocker.patch.object(mock_self, 'get_query_argument', side_effect=mock_get_query_argument)

    rucio_api_factory = RucioAPIFactory(None)
    mocker.patch.object(rucio_api_factory, 'for_instance', return_value=rucio)
    mock_self.rucio = rucio_api_factory

    mock_did_details = [
        {'status': 'OK', 'did': 'scope:name1', 'path': '/eos/user/rucio/scope:name1', 'size': 123},
        {'status': 'OK', 'did': 'scope:name2', 'path': '/eos/user/rucio/scope:name2', 'size': 456}
    ]

    class MockReplicaModeHandler(ReplicaModeHandler):
        def get_did_details(self, scope, name, force_fetch=False):
            return mock_did_details

    mocker.patch('rucio_jupyterlab.handlers.did_details.ReplicaModeHandler', MockReplicaModeHandler)

    def finish_side_effect(output):
        finish_json = json.loads(output)
        assert finish_json == mock_did_details, "Invalid finish response"

    mocker.patch.object(mock_self, 'finish', side_effect=finish_side_effect)

    DIDDetailsHandler.get(mock_self)

    calls = [call('namespace'), call('poll', '0'), call('did')]
    mock_self.get_query_argument.assert_has_calls(calls, any_order=True)  # pylint: disable=no-member
    rucio_api_factory.for_instance.assert_called_once_with(mock_active_instance)  # pylint: disable=no-member
