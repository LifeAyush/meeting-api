from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
from sklearn.cluster import AgglomerativeClustering

encoder = VoiceEncoder()

def get_speaker_embeddings(audio_np_array, sample_rate):
    wav = preprocess_wav(audio_np_array, sample_rate)
    return encoder.embed_utterance(wav)

def cluster_embeddings(embeddings, num_speakers=None):
    clustering = AgglomerativeClustering(n_clusters=num_speakers or 2)
    return clustering.fit_predict(embeddings)
