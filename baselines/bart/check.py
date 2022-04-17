from transformers import MBartForConditionalGeneration, MBart50TokenizerFast


def check(text):
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded, forced_bos_token_id=tokenizer.lang_code_to_id["uk_UA"]
    )
    batch = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return batch[0]


if __name__ == "__main__":
    model = MBartForConditionalGeneration.from_pretrained("output/checkpoint-1000")
    tokenizer = MBart50TokenizerFast.from_pretrained("output/checkpoint-1000", src_lang="uk_UA", tgt_lang="uk_UA")

    check("привіт як твої справи")
