#!/usr/bin/env python3
import argparse
import glob
import json


def prepare_dataset(data_dir, valid_size=3000):
    src_lines, tgt_lines = read_parallel(data_dir)

    src_train = src_lines[:-valid_size]
    tgt_train = tgt_lines[:-valid_size]
    write_jsonlines(src_train, tgt_train, "train.json")

    src_valid = src_lines[-valid_size:]
    tgt_valid = tgt_lines[-valid_size:]
    write_jsonlines(src_valid, tgt_valid, "valid.json")


def read_parallel(data_dir):
    src_files = glob.glob(f"{data_dir}/train/source-sentences/*.src.txt")
    tgt_files = glob.glob(f"{data_dir}/train/target-sentences/*.a1.txt")
    src_files.sort()
    tgt_files.sort()
    src_lines = []
    tgt_lines = []

    for s, t in zip(src_files, tgt_files):
        with open(s) as f:
            s_lines = f.readlines()
        with open(t) as f:
            t_lines = f.readlines()

        if len(s_lines) == len(t_lines):
            src_lines += s_lines
            tgt_lines += t_lines
        else:
            print(f"Skipping {s} ({len(s_lines)} lines in source, "
                  f"{len(t_lines)} in target)")

    assert len(src_lines) == len(tgt_lines)
    return src_lines, tgt_lines

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
            }, ensure_ascii=False)
            f_out.write(jsonline + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", help="Path to the UA-GEC `data` dir")
    args = parser.parse_args()

    prepare_dataset(args.data_dir)
