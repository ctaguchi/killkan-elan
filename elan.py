import sys
import re
import argparse

# ASR
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import numpy as np
import pydub
import torch

# for post-editing
from openai import OpenAI
import dotenv
dotenv.load_dotenv()

model_dir = "models/"


def read_annotations(input_tier) -> list:
    """
    Read in the annotations from the input tier XML file.

    Args:
        input_tier: The path to the input tier XML file.

    Returns:
        A list of dictionaries, where each dictionary represents an
        annotation with keys 'start', 'end', and 'value'.
    """
    annotations = []
    with open(input_tier, "r", encoding="utf-8") as input_tier:
        for line in input_tier:
            match = re.search(r'<span start="(.*?)" end="(.*?)"><v>(.*?)</v>', line)
            if match:
                annotation = {
                    "start": int(float(match.group(1)) * 1000),
                    "end": int(float(match.group(2)) * 1000),
                    "value": match.group(3)
                }
                annotations.append(annotation)
    return annotations


def predict(model: Wav2Vec2ForCTC,
            processor: Wav2Vec2Processor,
            audio: np.array) -> str:
    """
    Predict the transcription of an audio clip.

    Args:
        model: The model to use for prediction.
        processor: The processor to use for prediction.
        audio: The audio clip to transcribe.
    """
    input_dict = processor(audio,
                           return_tensors="pt",
                           padding=True,
                           sampling_rate=16000)
    with torch.no_grad():
        logits = model(input_dict.input_values).logits
    pred_ids = torch.argmax(logits, dim=-1)

    return processor.batch_decode(pred_ids)[0]


def llm_post_editing(text: str) -> str:
    """
    Post-edit the recognized text using the LLM model.

    Args:
        text: The recognized text to post-edit.

    Returns:
        The post-edited text.
    """
    model = "gpt-4o-2024-08-06"

    system_prompt = (
        "You will be given an ASR transcript in Kichwa, and your task is to correct any errors in the transcript. "
        "You can also add punctuation and capitalization as needed. "
        "Please output only the corrected transcript."
    )
    user_prompt = f"{text}"

    client = OpenAI()
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]
    
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return completion.choices[0].message.content


def main():
    """
    The main function of the script. This is where the script reads in
    all of the parameters that ELAN passes to the script, reads in the
    annotations from the input tier XML file, processes the audio for
    each annotation, and writes the results back to the output tier XML
    file.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_type",
                        type=str,
                        default="wav",
                        help="The type of file to process.")
    parser.add_argument("--llm_postedit",
                        action="store_true",
                        help="Whether to use LLM post-editing.")
    args = parser.parse_args()

    params = {}
    for line in sys.stdin:
        match = re.search(r'<param name="(.*?)".*?>(.*?)</param>', line)
        if match:
            params[match.group(1)] = match.group(2).strip()
    print("Parameter loaded", flush=True)

    if not params.get("output_tier"):
        print("ERROR: no `output_tier` specified", flush=True)
        sys.exit(-1)

    annotations = read_annotations(params["input_tier"])

    audio = pydub.AudioSegment.from_file(params["source"],
                                         format=args.file_type)
    converted_audio = audio.set_frame_rate(16000).set_channels(1)

    # Model/Processor loading
    model = Wav2Vec2ForCTC.from_pretrained(model_dir)
    processor = Wav2Vec2Processor.from_pretrained(model_dir)
    print("Model and processor loaded", flush=True)

    # Process the generated transcripts
    num_annotations = len(annotations)
    for (i, a) in enumerate(annotations):
        # Extract the audio for the current annotation
        clip = converted_audio[a["start"]:a["end"]]
        samples = clip.get_array_of_samples()

        # Convert the audio to a numpy array
        # The audio is normalized to the range [-1, 1].
        speech = np.array(samples).T.astype(np.float32) / np.iinfo(samples.typecode).max
        output = predict(model, processor, speech)
        print(f"Output: {output}", flush=True)

        # Post-edit the recognized text using the LLM model
        if args.llm_postedit:
            output = llm_post_editing(output)
            print(f"Post-edited: {output}", flush=True)

        a["output"] = output
        print(f"Processed {i + 1}/{num_annotations} annotations", flush=True)

    # Write the results back to the output tier XML file
    with open(params["output_tier"], "w", encoding="utf-8") as output_tier:
        # Write the document header
        output_tier.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output_tier.write('<TIER xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="file:avatech-tier.xsd" columns="XLS-R-ELAN-Output">\n')

        # Write out the recognized text
        for a in annotations:
            start = a["start"]
            end = a["end"]
            value = a["output"]
            output_tier.write(
                f'    <span start="{start}" end="{end}"><v>{value}</v></span>\n'
            )
        
        output_tier.write('</TIER>\n')
    
    # Tell ELAN that we're done.
    print("RESULT: DONE.")


if __name__ == "__main__":
    main()