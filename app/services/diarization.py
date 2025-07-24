import numpy as np
from resemblyzer import VoiceEncoder, preprocess_wav
from sklearn.cluster import AgglomerativeClustering

encoder = VoiceEncoder()


def get_speaker_embeddings(audio_np_array: np.ndarray, sample_rate: int) -> np.ndarray:
    """Extract speaker embeddings from an audio numpy array."""
    wav = preprocess_wav(audio_np_array, sample_rate)
    return encoder.embed_utterance(wav)


def cluster_embeddings(embeddings: np.ndarray, num_speakers: int = None) -> np.ndarray:
    """Cluster embeddings to group speakers. Returns cluster labels."""
    clustering = AgglomerativeClustering(n_clusters=num_speakers or 2)
    return clustering.fit_predict(embeddings)
