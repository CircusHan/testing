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
def question():
    word = random.choice(WORDS)
    correct = word['word']
    # prepare options
    others = random.sample([w['word'] for w in WORDS if w['word'] != correct], 3)
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
