#!/usr/bin/python3

import json
import click

@click.command(name="print-categories")
@click.argument('rubric_file', type=click.File())
def cmd(rubric_file):

    rubric = json.load(rubric_file)

    print("="*80)
    print(rubric["name"])
    for c in rubric["categories"]:
        for sc in c["subcategories"]:
            print(" - ", sc["cid"])

    print("="*80)

if __name__ == "__main__":
    cmd()