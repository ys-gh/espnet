import argparse
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pyopenjtalk
import torch

import text_processing as texp
from espnet2.bin.tts_inference import Text2Speech
from espnet2.tasks.tts import TTSTask
from espnet2.text.token_id_converter import TokenIDConverter

prosodic = False

parser = argparse.ArgumentParser()

parser.add_argument("--model_tag")
parser.add_argument("--train_config")
parser.add_argument("--model_file")
parser.add_argument("--vocoder_tag")
parser.add_argument("--vocoder_config")
parser.add_argument("--vocoder_file")
parser.add_argument("-p", "--prosodic", help="Prosodic text input mode", action="store_true")
parser.add_argument("--fs", type=int, default=24000)

args = parser.parse_args()

os.chdir('../')

# Case 2: Load the local model and the pretrained vocoder
print("download model = ", args.model_tag, "\n")
print("download vocoder = ", args.vocoder_tag, "\n")
print("モデルを読み込んでいます...\n")
if args.model_tag is not None:
    text2speech = Text2Speech.from_pretrained(
        model_tag=args.model_tag,
        vocoder_tag=args.vocoder_tag,
        device="cuda",
    )
elif args.vocoder_tag is not None:
    text2speech = Text2Speech.from_pretrained(
        train_config=args.train_config,
        model_file=args.model_file,
        vocoder_tag=args.vocoder_tag,
        device="cuda",
    )
else:
    text2speech = Text2Speech.from_pretrained(
        train_config=args.train_config,
        model_file=args.model_file,
        vocoder_config=args.vocoder_config,
        vocoder_file=args.vocoder_file,
        device="cuda",
    )

guide = "セリフを入力してください"
if args.prosodic:
    guide = "アクセント句がスペースで区切られた韻律記号(^)付きのセリフをすべてひらがなで入力してください。(スペースや記号もすべて全角で)\n"
x = ""
while (1):
    # decide the input sentence by yourself
    print(guide)

    x = input()
    if x == "exit":
        break

    #model, train_args = TTSTask.build_model_from_file(
    #        args.train_config, args.model_file, "cuda"
    #        )

    token_id_converter = TokenIDConverter(
        token_list=text2speech.train_args.token_list,
        unk_symbol="<unk>",
    )

    text = x
    if args.prosodic:
        tokens = texp.a2p(x)
        text_ints = token_id_converter.tokens2ids(tokens)
        text = np.array(text_ints)
    else:
        print("\npyopenjtalk_accent_with_pauseによる解析結果：")
        print(texp.text2yomi(x), "\n")

    # synthesis
    with torch.no_grad():
        start = time.time()
        data = text2speech(text)
        wav = data["wav"]
        #print(text2speech.preprocess_fn("<dummy>",dict(text=x))["text"])
    rtf = (time.time() - start) / (len(wav) / text2speech.fs)
    print(f"RTF = {rtf:5f}")

    if not os.path.isdir("generated_wav"):
        os.makedirs("generated_wav")

    if args.model_tag is not None:
        if "tacotron" in args.model_tag:
            mel = data['feat_gen_denorm'].cpu()
            plt.imshow(torch.t(mel).numpy(),
                       aspect='auto',
                       origin='lower',
                       interpolation='none',
                       cmap='viridis')
            plt.savefig('generated_wav/' + x + '.png')
    else:
        if "tacotron" in args.model_file:
            mel = data['feat_gen_denorm'].cpu()
            plt.imshow(torch.t(mel).numpy(),
                       aspect='auto',
                       origin='lower',
                       interpolation='none',
                       cmap='viridis')
            plt.savefig('generated_wav/' + x + '.png')

    # let us listen to generated samples
    import numpy as np
    from IPython.display import Audio, display

    #display(Audio(wav.view(-1).cpu().numpy(), rate=text2speech.fs))
    #Audio(wav.view(-1).cpu().numpy(), rate=text2speech.fs)
    np_wav = wav.view(-1).cpu().numpy()

    print("サンプリングレート", args.fs, "で出力します。")
    from scipy.io.wavfile import write
    samplerate = args.fs
    t = np.linspace(0., 1., samplerate)
    amplitude = np.iinfo(np.int16).max
    data = amplitude * np_wav / np.max(np.abs(np_wav))
    write("generated_wav/" + x + ".wav", samplerate, data.astype(np.int16))
    print("\n\n\n")
