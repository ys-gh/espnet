model_tag="kan-bayashi/jsut_tacotron2_accent_with_pause"
train_config=""
model_file=""

vocoder_tag="parallel_wavegan/jsut_hifigan.v1"
vocoder_config=""
vocoder_file=""

prosodic="false"
fs=""

. ../utils/parse_options.sh

COMMAND="python tts_inference_with_accent.py "


pwg=`pip list | grep parallel`
if [ "$pwg" == "" ];
then
	pip install -U parallel_wavegan
fi

ip=`pip list | grep ipython`
if [ "$pwg" == "" ];
then
	pip install -U IPython
fi


if [ "$train_config" == "" ] && [ "$model_file" == "" ]
then
	COMMAND="${COMMAND}--model_tag \"${model_tag}\" "
else
	COMMAND="${COMMAND}--train_config \"${train_config}\" "
	COMMAND="${COMMAND}--model_file \"${model_file}\" "
fi

if [ "$vocoder_config" == "" ] && [ "$vocoder_file" == "" ]
then
	COMMAND="${COMMAND}--vocoder_tag \"${vocoder_tag}\" "
else
	COMMAND="${COMMAND}--vocoder_config \"${vocoder_config}\" "
	COMMAND="${COMMAND}--vocoder_file \"${vocoder_file}\" "
fi

if [ ! "$fs" == "" ]; then COMMAND="${COMMAND}--fs ${fs} "; fi

if [ "$prosodic" == "true" ]; then COMMAND="${COMMAND}-p"; fi

echo "${COMMAND}"
echo ""
echo ""

eval $COMMAND
