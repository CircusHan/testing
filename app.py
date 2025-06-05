from flask import Flask, render_template, jsonify, request, session
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
