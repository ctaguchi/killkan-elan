# ELAN extension for Kichwa speech recognition
This is an ELAN extension for Kichwa speech recognition.
The backbone speech recognizer is a fine-tuned version of Wav2Vec2-XLS-R-300M, and takes up approximately 1.2GB.
Note that this repo does not have the speech recognition model itself due to its large file size.
You will need to download the model by yourself.
The model can be downloaded from the Hugging Face Hub: https://huggingface.co/ctaguchi/killkan-xls-r-300m
Please contact the author (Chihiro Taguchi) if you need help with getting the model.

## How to add the extension to your ELAN
1. Install this git repository
1. Create the `models` directory (`mkdir models`)
1. Move the model files under the `models` directory. Necessary files are: `added_tokens.json`, `model.safetensors`, `special_tokens_map.json`, `vocab.json`, `config.json`, `preprocessor_config.json`, and `tokenizer_config.json`.
1. You need Python to run this extension.
  - If you don't have one, please install Python 3.9 from the [official release](https://www.python.org/downloads/).
  - If you have it already, make sure to use Python version 3.9. If your version is not 3.9 (you can check it by running `python --version` on your terminal), It is recommended to switch the version to 3.9 with [pyenv](https://github.com/pyenv/pyenv) by running `pyenv local 3.9` on your terminal.
1. Once you have the correct Python version, install the necessary libraries by running `poetry install`.
1. If you are using MacOS, open your Finder, go to "Applications" from the tab on the left, right-click (or two-finger click) on the ELAN app, select "Show Package Contents", and go to Contents > app > extensions, and copy this repository (killkan-elan) under "extensions".
1. Open your ELAN (or restart it if you already have it open).
1. Load your media (only wav is supported by this recognizer).
1. You should now be able to find "XLS-R Kichwa Killkan" as one of your recognizers. If you cannot find the recognizer tab in the Viewer, you can add it from View > Viewer, and make sure "Recognizer" is checked.

## Debug
- If you encounter any error when running the speech recognizer in ELAN, you can read the detailed error (e.g., from Python) by clicking on the Report button next to the Start button.
- If your filename contains a whitespace, the recognizer program might not be able to find your annotation file. Make sure to have no whitespace characters; substitute them with underscores (_) if necessary.

## Contact
Chihiro Taguchi: chihirot at nd.edu