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
    export HELP_THIS_BOOK=1  # Tell book_magics.py to adjust rendering
    # Remove --no-cache for faster rendering:
    quarto render book/ --no-cache --profile helpthisbook --to gfm --output-dir $PWD/_helpthisbook/
    rm _helpthisbook/index.html
    rm -f _helpthisbook/book.zip

    # We want lexical order to match semantic order:
    cd _helpthisbook
    mv -f index.md part_00.md
    rm -rf part_99/
    mv appendices/ part_99/
    cd ..

    INPUT_CHAPTERS=$(cat book/_quarto.yml | grep .qmd | grep -v '#' | wc -l)
    OUTPUT_CHAPTERS=$(find _helpthisbook -iname '*.md' | wc -l)
    if [ ! $INPUT_CHAPTERS == $OUTPUT_CHAPTERS ]
    then
        echo "WRONG NUMBER OF CHAPTERS: IN $INPUT_CHAPTERS OUT $OUTPUT_CHAPTERS"
        exit 1
    fi

    cd _helpthisbook
    zip book.zip $(find part_* | sort )
