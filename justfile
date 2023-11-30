venv:
    python3.11 -m venv venv
    # TODO pin requirements.txt?
    venv/bin/pip install -r requirements.txt

preview:
    . venv/bin/activate && PYTHONPATH=$PWD/src quarto preview book

wc:
    wc --words book/*.qmd
