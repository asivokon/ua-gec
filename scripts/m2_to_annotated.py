#!/usr/bin/env python3
"""Convert .m2 file to the annotated format.
"""
import argparse
import sys
from dataclasses import dataclass
from typing import Iterable, Optional

import pytest
from ua_gec import AnnotatedText
from ua_gec.annotated_text import OverlapError


@dataclass
class M2Annotation:
    start_index: int
    end_index: int
    replacement: str
    error_type: str
    annotator_id: int


@dataclass
class M2Sentence:
    source: str
    annotations: list[M2Annotation]


def read_m2(
    lines: Iterable[str], annotator: Optional[int] = None
) -> Iterable[M2Sentence]:
    current = None
    for line in lines:
        line = line.rstrip("\n")

        if line.startswith("S "):
            assert not current
            source = line.removeprefix("S ")
            current = M2Sentence(source, [])

        elif line.startswith("A "):
            span, error_type, repl, _, _, annotator_id = line.split("|||")
            start = int(span.split()[1])
            end = int(span.split()[2])
            if repl == "-NONE-":
                repl = ""
            annotator_id = int(annotator_id)
            ann = M2Annotation(
                start_index=start,
                end_index=end,
                replacement=repl,
                error_type=error_type,
                annotator_id=annotator_id,
            )
            if error_type != "noop":
                if annotator is None or annotator_id == annotator:
                    current.annotations.append(ann)

        elif not line:
            assert current is not None
            yield current
            current = None

        else:
            raise ValueError(f"Unexpected line in the .m2 file: {line}")


def m2_to_annotated(m2_sent: M2Sentence) -> AnnotatedText:
    annotated = AnnotatedText(m2_sent.source)
    for m2_ann in m2_sent.annotations:
        start = token_to_character_position(m2_sent.source, m2_ann.start_index)
        end = token_to_character_position(m2_sent.source, m2_ann.end_index)

        ####### HACK: There should be a better way to handle trailing whitespace
        try:
            if m2_sent.source[end - 1] == " ":
                end -= 1
        except IndexError:
            pass
        end = max(start, end)
        ########################################################################

        meta = {"error_type": m2_ann.error_type}
        repl = m2_ann.replacement
        if start == end and repl == ",":
            repl = ", "
        annotated.annotate(start, end, repl, meta=meta)
    return annotated


def token_to_character_position(s: str, token_pos: int) -> int:
    char_pos = 0
    while token_pos:
        token_pos -= 1
        char_pos = s.find(" ", char_pos) + 1
        if char_pos == 0:
            if token_pos > 0:
                raise IndexError(f"Token is outside of the string")
            else:
                char_pos = len(s)
    return char_pos


def test_token_to_character_position():
    s = "Привіт , світе !"

    # Tokens within the string
    assert token_to_character_position(s, 0) == 0
    assert token_to_character_position(s, 1) == 7
    assert token_to_character_position(s, 2) == 9
    assert token_to_character_position(s, 3) == 15

    # Token number N + 1 (where N is the number of tokens in s)
    assert token_to_character_position(s, 4) == len(s)

    # Token number N + 2 and beyond
    with pytest.raises(IndexError):
        token_to_character_position(s, 5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("m2_path")
    parser.add_argument("-o", "--output")
    parser.add_argument("--annotator", type=int, default=0)
    parser.add_argument(
        "--ignore-errors",
        action="store_true",
        help="Skip sentences with annototation errors. This is a temporary hack.",
    )
    args = parser.parse_args()

    f_in = open(args.m2_path, encoding="utf8")
    f_out = open(args.output, 'w', encoding="utf8") if args.output else sys.stdout

    for i, m2_sent in enumerate(read_m2(f_in, annotator=args.annotator)):
        try:
            annotated = m2_to_annotated(m2_sent)
        except OverlapError as e:
            print(f"Error in sentence #{i}: {e}", file=sys.stderr)
            if not args.ignore_errors:
                sys.exit(1)
        f_out.write(annotated.get_annotated_text() + "\n")


if __name__ == "__main__":
    main()
