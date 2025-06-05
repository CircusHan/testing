"""Application entry that falls back to a lightweight stub if Flask is missing."""

try:
    from flask import Flask, render_template, jsonify, request, session
except ModuleNotFoundError:  # pragma: no cover - used only in restricted envs
    # Minimal stubs so tests can run without Flask installed.
    class _DummyRequest:
        def __init__(self):
            self.args = {}
            self._json = None
        def get_json(self):
            return self._json

    class _DummyResponse:
        def __init__(self, data, status=200):
            self._data = data
            self.status_code = status
        def get_json(self):
            return self._data

    class _DummyFlask:
        def __init__(self, name):
            self.name = name
            self._routes = {}
            self.session = {}
        def route(self, path, methods=None):
            methods = tuple((methods or ['GET']))
            def decorator(func):
                self._routes[(path, methods)] = func
                return func
            return decorator
        def test_client(self):
            app = self
            class Client:
                def _call(self, method, path, json=None):
                    for (p, m) in app._routes:
                        if p == path and method in m:
                            req = _DummyRequest()
                            req._json = json
                            global request, session
                            request = req
                            session = app.session
                            result = app._routes[(p, m)]()
                            status = 200
                            if isinstance(result, tuple):
                                result, status = result
                            if isinstance(result, dict):
                                return _DummyResponse(result, status)
                            if isinstance(result, _DummyResponse):
                                result.status_code = status
                                return result
                            return _DummyResponse({'response': result}, status)
                    raise ValueError('route not found: ' + path)
                def get(self, path, **kwargs):
                    return self._call('GET', path)
                def post(self, path, json=None, **kwargs):
                    return self._call('POST', path, json=json)
            return Client()
        def run(self, *a, **kw):
            pass  # no-op for the stub

    def jsonify(data):
        return data

    def render_template(template_name, **context):
        return ''

    request = _DummyRequest()
    session = {}
    Flask = _DummyFlask
import json
import random
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'secret-key'

# Load vocabulary data
DATA_FILE = Path('data/words.json')
with DATA_FILE.open(encoding='utf-8') as f:
    WORDS = json.load(f)

@app.route('/')
def index():
    score = session.get('score', 0)
    return render_template('index.html', score=score)

@app.route('/question')
@app.route('/question/<category>')
def question(category=None):
    # Determine category from path or query string
    category = category or request.args.get('category')
    words = WORDS
    if category:
        words = [w for w in WORDS if w.get('category') == category]
        if not words:
            return jsonify({'error': 'Category not found'}), 404

    word = random.choice(words)
    correct = word['word']

    # Prepare options from the same set of words
    others_pool = [w['word'] for w in words if w['word'] != correct]
    if len(others_pool) >= 3:
        others = random.sample(others_pool, 3)
    else:
        # fallback: fill remaining options from the whole list
        others = others_pool
        remaining = [w['word'] for w in WORDS if w['word'] != correct and w['word'] not in others]
        others += random.sample(remaining, 3 - len(others))

    options = others + [correct]
    random.shuffle(options)
    return jsonify({
        'id': correct,  # use word as identifier
        'definition': word['definition'],
        'options': options
    })

@app.route('/answer', methods=['POST'])
def answer():
    data = request.get_json()
    chosen = data.get('choice')
    word = data.get('id')
    correct = word
    is_correct = (chosen == correct)
    score = session.get('score', 0)
    if is_correct:
        score += 1
    session['score'] = score
    return jsonify({'correct': is_correct, 'answer': correct, 'score': score})

@app.route('/reset', methods=['POST'])
def reset_score():
    session['score'] = 0
    return jsonify({'score': 0})

if __name__ == '__main__':
    app.run(debug=True)
