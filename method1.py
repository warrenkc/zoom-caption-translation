#!/usr/bin/env python

# [START speech_transcribe_streaming_mic]
from __future__ import division
import requests
import re
import sys
import six
import time
import json
from google.cloud import translate_v2 as translate
from google.cloud import speech_v1p1beta1 as speech


import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
translate_client = translate.Client()



class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk,_configs):
        self._rate = rate
        self._chunk = chunk
        self.source = _configs["source_lang"]
        self.target = _configs["target_lang"]
        self.seq_count=0
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()
    
    def zoomtranslate(self,text):
        if isinstance(text, six.binary_type):
            text = text.decode("utf-8")
        result =translate_client.translate(text,source_language=self.source,target_language=self.target)
  
        return result["translatedText"]

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)
     


def listen_print_loop(responses,token,stream):
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        
        result = response.results[0]
        if not result.alternatives:
            continue
        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write("Speech:"+transcript + overwrite_chars + "\r")
            sys.stdout.flush()
            num_chars_printed = len(transcript)
        else:
            print("Speech:",transcript + overwrite_chars)
            sentence=transcript + overwrite_chars
            
            print("Translate:",stream.zoomtranslate(sentence),"\n")

            sentence=sentence+"\n"+stream.zoomtranslate(sentence)
            post_params={
                'seq' : stream.seq_count,
                'lang':"en-US"}
            headers={'Content-type': 'text/plain; charset=utf-8'}
            if stream.seq_count == 0:
                session = requests.Session()
            s=time.time()
            result=session.post(token,params=post_params, data=sentence.encode('utf-8'),headers=headers)
            print(f"第{stream.seq_count}次傳送花費：{time.time()-s:.2f}")
            if result.status_code!=200:
                print(">>錯誤！訊息為傳送出去！")
            stream.seq_count=stream.seq_count+1
            num_chars_printed = 0


def main():
    token=input("請輸入zoom API憑證：")
    print()
    with open('config.json') as config:
        _configs = json.load(config)
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.

    # 請在這裡放入常用語詞進行判斷
    phrases = ["中央長老團","會眾","分區監督","分部委員會"] 
    boost = 20.0
    speech_contexts_element = {"phrases": phrases, "boost": boost}
    speech_contexts = [speech_contexts_element]
    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        speech_contexts=speech_contexts,
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=_configs["source_lang"],
        enable_automatic_punctuation=True
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    print("請開始說話.............. (結束請按下ctrl+c)：")
    print()
    with MicrophoneStream(RATE, CHUNK,_configs) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        
        listen_print_loop(responses,token,stream)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('---------------------結束程式---------------------')
        sys.exit(0)
# [END speech_transcribe_streaming_mic]
