from transformers import Wav2Vec2Model, Wav2Vec2Processor
import audio_transformers
import torch
import librosa
from pathlib import Path
import pandas as pd
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

extractor = AutoFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")
model = AutoModelForAudioClassification.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"  # Can change the csv_file path here
csv_file = str(csv_file)

df = pd.read_csv(csv_file)
song_links = df['spotify_link']

audio, sr = librosa.load('', sr= 16000)
