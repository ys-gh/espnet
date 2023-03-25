import time

import numpy as np
import torch

import text_processing as texp
from espnet2.bin.tts_inference import Text2Speech
from espnet2.text.token_id_converter import TokenIDConverter

fs, lang = 44100, "Japanese"
model = "./espnet/egs2/CHARACTER/tts1/exp/tts_finetune_vits_raw_phn_jaconv_pyopenjtalk_accent_with_pause"

text2speech = Text2Speech.from_pretrained(
    model_file=model,
    device="cpu",
    speed_control_alpha=1.0,
    noise_scale=0.333,
    noise_scale_dur=0.333,
)

while (1):
    x = input()

    if x == "exit":
        break

    token_id_converter = TokenIDConverter(
        token_list=text2speech.train_args.token_list,
        unk_symbol="<unk>",
    )

    tokens = texp.a2p(x)
    text_ints = token_id_converter.tokens2ids(tokens)
    text = np.array(text_ints)

    with torch.no_grad():
        start = time.time()
        data = text2speech(text)
        wav = data["wav"]
        #print(text2speech.preprocess_fn("<dummy>",dict(text=x))["text"])
    rtf = (time.time() - start) / (len(wav) / text2speech.fs)
    print(f"RTF = {rtf:5f}")
