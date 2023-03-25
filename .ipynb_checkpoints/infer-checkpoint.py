import time

import torch

from espnet2.bin.tts_inference import Text2Speech

fs, lang = 44100, "Japanese"
model = "./espnet/egs2/CHARACTER/tts1/exp/tts_finetune_vits_raw_phn_jaconv_pyopenjtalk_accent_with_pause"
