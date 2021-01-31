import os
from pydub import AudioSegment
import wave
import time
import speech_recognition as sr
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="hack-uci-2021-152c1928ead5.json"

from google.cloud import storage
from google.cloud import speech

""" Upload data to a bucket"""
def upload_to_bucket(blob_name, path_to_file, bucket_name):
    # Explicitly use service account credentials by specifying the private key file.
    storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(path_to_file)
    #returns a public url
    return blob.public_url

def video(file_name):
    storage_client = storage.Client.from_service_account_json("hack-uci-2021-152c1928ead5.json")
    bucket = storage_client.get_bucket("hack-uci-2021-bucket")
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    return blob.public_url

def frame_rate_channel(audio_file_name):
    with wave.open(audio_file_name, "rb") as wave_file:
        frame_rate = wave_file.getframerate()
        channels = wave_file.getnchannels()
        return frame_rate,channels

def stereo_to_mono(audio_file_name):
    sound = AudioSegment.from_wav(audio_file_name)
    sound = sound.set_channels(1)
    sound.export(audio_file_name, format = "wav" )
        

def google_transcribe(audio_file_name):
    file_path = audio_file_name
    frame_rate, channels = frame_rate_channel(file_path)
    if channels > 1:
        stereo_to_mono(file_path)
    video(audio_file_name)
    gcs_uri = "gs://hack-uci-2021-bucket/"+audio_file_name

    transcript = ''
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
        enable_automatic_punctuation=True)
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout = 90)
    for result in response.results:
        transcript += str(result.alternatives[0].transcript)
    return transcript

import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
 
def read_article(file_name):
    file = open(file_name, "r")
    file.seek(0)
    filedata = file.readlines()
    article = filedata[0].split(". ")
    sentences = []
    for sentence in article:
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    file.close()
    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
    all_words = list(set(sent1 + sent2))
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
    return similarity_matrix


def generate_summary(file_name, top_n=3):
    stop_words = stopwords.words('english')
    summarize_text = []
    whole_text = ""
    count = 1
    # Step 1 - Read text anc split it
    sentences =  read_article(file_name)
    print("sentences = ", sentences)
    for i in range(len(sentences)):
        for j in range(len(sentences[i])):
            whole_text = whole_text+" "+sentences[i][j]
    print(whole_text)
    if len(sentences) < top_n:
            top_n = len(sentences)
    if len(sentences) > 1:
        # Step 2 - Generate Similary Martix across sentences
        sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)
        # Step 3 - Rank sentences in similarity martix
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)
        for i in range(top_n):
            summarize_text.append(" ".join(ranked_sentence[i][1])) 
        
        for i in range(len(summarize_text)):
            summarize_text[i] = str(count) + ". " + summarize_text[i]
            count += 1
            # summarized = ("{}. {}".format(i, summarize_text[i]))
        print("Summarize Text: \n", ".\n ".join(summarize_text))
        return (whole_text, ".\n ".join(summarize_text))
    else:
        print("Summarize Text: \n 1.{}\n".format(" ".join(sentences[0])))
        return(whole_text, " ".join(sentences[0]))

if __name__ == "__main__":
    print("In Main")
    script = google_transcribe("history40b.wav")
    f = open("output.txt", "w")
    f.seek(0)
    f.write(script)
    f.close()
    generate_summary("./output.txt")