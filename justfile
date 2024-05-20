venv:
    python3.11 -m venv venv
    # TODO pin requirements.txt?
    venv/bin/pip install -r requirements.txt

preview:
    . venv/bin/activate && PYTHONPATH=$PWD/src quarto preview book

wc:
    wc --words book/**/*.qmd book/*.qmd

helpthisbook:
    #!/usr/bin/env bash
    set -euxo pipefail
    . venv/bin/activate
    export PYTHONPATH=$PWD/src
    export HELPTHISBOOK=1
    quarto render book/ --profile helpthisbook --to gfm --output-dir $PWD/_helpthisbook/
    rm _helpthisbook/index.html
    INPUT_CHAPTERS=$(cat book/_quarto.yml | grep .qmd | grep -v '#' | wc -l)
    OUTPUT_CHAPTERS=$(find _helpthisbook -iname '*.md' | wc -l)
    if [ ! $INPUT_CHAPTERS == $OUTPUT_CHAPTERS ]
    then
       echo "WRONG NUMBER OF CHAPTERS: IN $INPUT_CHAPTERS OUT $OUTPUT_CHAPTERS"
       exit 1
    fi
