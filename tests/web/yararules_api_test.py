"""Tests for the YaraRule API."""

import json
import pytest

from yeti.webapp import app

app.testing = True
client = app.test_client()

# pylint: disable=fixme
# TODO: Consider using pytest-flask for easier testing flask stuff, e.g.:
# - Access to url_for objects to test routes
# - Access to .json attribute of request

@pytest.mark.usefixtures("clean_db")
def test_index(populate_yara_rules):
    """Test that fetched Yara rules are well-formed"""
    names = [yr.name for yr in populate_yara_rules]
    for name in names:
        query_json = {'name': name}
        rv = client.post('/api/indicators/filter/',
                         data=json.dumps(query_json),
                         content_type='application/json')
        response = json.loads(rv.data)
        for element in response:
            assert isinstance(element['id'], int)
            assert len(element['pattern']) > 10

@pytest.mark.usefixtures("clean_db", "populate_yara_rules")
def test_yara_rule_creation():
    pattern = "rule yeti_rule { strings: $MZ = { 4D 5A } condition: $MZ}"
    query_json = {'name': 'test', 'pattern': pattern, 'type': 'indicator.yararule'}
    rv = client.post('/api/indicators/',
                     data=json.dumps(query_json),
                     content_type='application/json')
    response = json.loads(rv.data)
    assert rv.status_code == 200
    assert response['id'] is not None
    assert response['pattern'] == pattern

@pytest.mark.usefixtures("clean_db", "populate_yara_rules")
def test_invalid_yara_rule():
    """Test that Yara rules with invalid patterns cannot be created."""
    query_json = {'name': 'test', 'pattern': 'lol', 'type': 'indicator.yararule'}
    rv = client.post('/api/indicators/',
                     data=json.dumps(query_json),
                     content_type='application/json')
    response = json.loads(rv.data)
    assert rv.status_code == 400
    assert 'ValidationError' in response
    assert 'Could not compile yara rule' in response['ValidationError']

@pytest.mark.usefixtures("clean_db", "populate_yara_rules")
def test_no_yara_rule():
    """Test that Yara rules with empty patterns cannot be created."""
    query_json = {'name': 'test', 'type': 'indicator.yararule'}
    rv = client.post('/api/indicators/',
                     data=json.dumps(query_json),
                     content_type='application/json')
    response = json.loads(rv.data)
    assert rv.status_code == 400
    assert 'ValidationError' in response
    assert 'pattern' in response['ValidationError']
    assert "Missing data for required field." in response['ValidationError']['pattern']


MATCHING_TEST = [
    (b'MZ\x00\x00\x00\x00\x00\x00\x00', [{
        'name': 'MZ',
        'details': [{'bytes': {'b64': "b'TVo='"}, 'name': '$MZ', 'offset': 0}],
    }]),
    (b'PK\x00\x00\x00\x00\x00\x00\x00', []),
]

@pytest.mark.usefixtures('clean_db', 'populate_yara_rules')
def test_match_yara_rules():
    """Test that Regex can be matched through the API."""
    for obj, expected in MATCHING_TEST:
        query_json = {'object': obj}
        rv = client.post('/api/indicators/match', data=query_json)
        response = json.loads(rv.data)
        assert expected == response
        assert rv.status_code == 200
