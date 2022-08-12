#!/usr/bin/env python3
import argparse
import requests
import fileinput
import json

import ua_gec
from ua_gec.annotated_text import AnnotatedText


def check_text(text, api_address):
    """Check the text with a LanguageTool.

    Args:
        text (str): The text to check.
        api_address (str): The URL of the LanguageTool HTTP API.

    Returns:
        AnnotatedText: Text annotated for errors.

    """
    url = api_address.rstrip("/") + "/check"
    request = {"text": text, "language": "uk"}
    response = requests.post(url, params=request)
    response.raise_for_status()
    return annotate_from_response(text, response.json())


def annotate_from_response(text, response):
    """Annotate the text from a LanguageTool response.

    Args:
        text (str): The text to annotate.
        response (dict): The response from the LanguageTool HTTP API.

    Returns:
        AnnotatedText: Text annotated for errors.

    """
    annotated_text = AnnotatedText(text)
    for error in response["matches"]:
        if error["replacements"]:
            repl = error["replacements"][0]["value"]
            error_type = error["rule"]["issueType"]
            meta = {"error_type": error_type}
            annotated_text.annotate(
                error["offset"], error["offset"] + error["length"], repl, meta=meta
            )
    return annotated_text


def check_uagec(api_address):
    corpus = ua_gec.Corpus('all')
    for doc in corpus:
        annotated_text = check_text(doc.source, api_address)
        item = {
            "id": doc.id,
            "source": doc.source,
            "annotated_text": annotated_text.get_annotated_text(),
        }
        print(json.dumps(item))


def main():
    parser = argparse.ArgumentParser(description="Check the text with a LanguageTool.")
    parser.add_argument("text", help="Path to the text to check.", nargs="?")
    parser.add_argument(
        "--http-api",
        default="https://languagetool.org/api/v2",
        help="URL of the LanguageTool HTTP API.",
    )
    args = parser.parse_args()

    for line in fileinput.input(args.text):
        text = line.rstrip()
        annotated_text = check_text(text, args.http_api)
        print(str(annotated_text))


if __name__ == "__main__":
    #check_uagec("https://languagetool.org/api/v2")
    main()
