#!/usr/bin/env python3
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import fileinput


def check(text):
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded, forced_bos_token_id=tokenizer.lang_code_to_id["uk_UA"]
    )
    batch = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return batch[0]


if __name__ == "__main__":
    model = "./output/checkpoint-15000"
    tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50", src_lang="uk_UA", tgt_lang="uk_UA")
    model = MBartForConditionalGeneration.from_pretrained(model)

    check("привіт як твої справи")

    for line in fileinput.input():
        print(check(line))
