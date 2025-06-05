# Vocabulary Quiz App

This is a simple Flask application for testing English vocabulary. It displays a
Korean definition and multiple English words to choose from.

## Features

- **Word Categories** &ndash; focus on specific groups of words.
- **Scoring System** &ndash; keep track of how many answers you get right.
- **Improved Styling** &ndash; cleaner layout with basic CSS.

## Setup

Install the dependencies and start the development server:

```bash
pip install -r requirements.txt
python app.py
```

Open your browser at <http://localhost:5000> to start the quiz.

## Running Tests

This project uses `pytest` for testing. Once you have installed the
dependencies, run the test suite with:

```bash
pytest
```

There are currently no automated tests, but you can add them under a `tests/`
directory.

## Contributing

Contributions are welcome! To submit a change:

1. Fork the repository and create a new branch for your update.
2. Make your changes and add tests where appropriate.
3. Run `pytest` to ensure the test suite passes.
4. Open a pull request explaining your modifications.
