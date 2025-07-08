# MusiXQA
A well-annotated dataset of music sheet images designed for VQA in music understanding.
- Paper: [arXiv](https://arxiv.org/abs/2506.23009)

## Dataset
[MusiXQA](https://huggingface.co/datasets/puar-playground/MusiXQA) is a multimodal dataset for evaluating and training music sheet understanding systems. Each data sample is composed of:
- A music sheet image (`.png`) rendered by [MusiXTEX](https://texdoc.org/serve/musixtex/0).
- Its corresponding MIDI file (`.mid`) 🎵
- A structured annotation (from `metadata.json`)
- Question–Answer (QA) pairs targeting musical structure, semantics, and optical music recognition (OMR)

## Installation
This code is written in python 3.10. 
```
conda create -n MusiXQA python=3.10
pip install -r requirements.txt
```

To compile the latex file, please install the following:
```
sudo apt install texlive-latex-base
sudo apt install texlive-music
sudo apt-get install texlive-lang-all
sudo apt-get install texlive-fonts-recommended texlive-fonts-extra
```

The code also includes a MIDI to Audio function, which requires the [fluidsynth](https://github.com/FluidSynth/fluidsynth) software. And converting to mp3 requires `ffmpeg`. Install by running:
```
brew install fluidsynth
brew install ffmpeg
```
To generate audio, a soundfont in `.sf2` format is required. For higher quality, please download a larger version online. 


## Model
[Phi-3-MusiX](https://huggingface.co/puar-playground/Phi-3-MusiX) is a LoRA adapter for [microsoft/Phi-3-vision-128k-instruct](https://huggingface.co/microsoft/Phi-3-vision-128k-instruct) for understanding symbolic music in the form of scanned music sheets, MIDI files, and structured annotations. This adapter equips Phi-3 with the ability to perform symbolic music reasoning and answer questions about scanned music sheets and MIDI content.

### Fine-tune the model
You can use the `loraft_phi3v.py` script to finetune the phi-3-vision model. Please replace "xxxxxxxx" with your token for huggingface and wandb.
```
deepspeed --num_gpus=8 loraft_phi3v.py --deepspeed ds_config.json --hf_token xxxxxxxx --wandb_token xxxxxxxx
```

## Data Synthesis
run the script `generate_musicsheet.py`. The code will save music sheet in pdf and the config file in specified directory. The pdf is compiled by [MusixTex](https://texdoc.org/serve/musixtex/0). The output will be saved in the `./data` folder, including 
```
config.yaml 
ground-truth music (`.json`)
PDF document (.pdf)
page images (.png), 
MIDI (`.mdi`)
Audio (`.mp3`)
```


## 🎓 Reference
If you use this dataset in your work, please cite it using the following reference:
```
@article{chen2025musixqa,
  title={MusiXQA: Advancing Visual Music Understanding in Multimodal Large Language Models},
  author={Chen, Jian and Ma, Wenye and Liu, Penghang and Wang, Wei and Song, Tengwei and Li, Ming and Wang, Chenguang and Zhang, Ruiyi and Chen, Changyou},
  journal={arXiv preprint arXiv:2506.23009},
  year={2025}
}
```
