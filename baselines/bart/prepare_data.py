#!/usr/bin/env python3
import argparse
import fileinput
import glob
import json


def prepare_dataset(data_dir, valid_size=3000):
    src_files = glob.glob(f"{data_dir}/train/source-sentences/*")
    tgt_files = glob.glob(f"{data_dir}/train/target-sentences/*")
    for s, t in zip(src_files, tgt_files):
        with open(s) as f:
            s_lines = f.readlines()
        with open(t) as f:
            t_lines = f.readlines()

        if len(s_lines) != len(t_lines):
            print(s)



    src_lines = list(fileinput.input(src_files))
    tgt_lines = list(fileinput.input(tgt_files))
    print(len(src_files))
    print(len(tgt_files))
    assert len(src_lines) == len(tgt_lines)

    src_train = src_lines[:-valid_size]
    tgt_train = tgt_lines[:-valid_size]
    write_jsonlines(src_train, tgt_train, "train.json")

    src_valid = src_lines[-valid_size:]
    tgt_valid = tgt_lines[-valid_size:]
    write_jsonlines(src_valid, tgt_valid, "valid.json")


def write_jsonlines(src_lines, tgt_lines, out_path):
    with open(out_path, "wt") as f_out:
        for src, tgt in zip(src_lines, tgt_lines):
            src = src.strip("\n")
            tgt = tgt.strip("\n")
            if not src and not tgt:
                continue
            jsonline = json.dumps({
                "translation": {
                    "src": src,
                    "tgt": tgt,
                }
            })
            f_out.write(jsonline + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help="Path to the UA-GEC `data` dir")
    args = parser.parse_args()

    prepare_dataset(args.data_dir)
