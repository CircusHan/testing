import json
from app import app

def test_question_structure():
    client = app.test_client()
    resp = client.get('/question')
    assert resp.status_code == 200
    data = resp.get_json()
    assert {'id', 'definition', 'options'} <= data.keys()
    assert isinstance(data['id'], str)
    assert isinstance(data['definition'], str)
    assert isinstance(data['options'], list)
    assert data['id'] in data['options']
    assert len(data['options']) == 4

def test_answer_evaluation():
    client = app.test_client()
    q_resp = client.get('/question')
    question = q_resp.get_json()

    correct_choice = question['id']
    wrong_choice = next(opt for opt in question['options'] if opt != correct_choice)

    # correct answer
    resp_correct = client.post('/answer', json={'id': question['id'], 'choice': correct_choice})
    data_correct = resp_correct.get_json()
    assert resp_correct.status_code == 200
    assert data_correct['correct'] is True
    assert data_correct['answer'] == correct_choice

    # wrong answer
    resp_wrong = client.post('/answer', json={'id': question['id'], 'choice': wrong_choice})
    data_wrong = resp_wrong.get_json()
    assert resp_wrong.status_code == 200
    assert data_wrong['correct'] is False
    assert data_wrong['answer'] == correct_choice

