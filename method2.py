# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Cloud Media Translation API sample application using a microphone.

Example usage:
    python translate_from_mic.py
"""

# [START media_translation_translate_from_mic]
from __future__ import division
import requests
import time
import sys
import itertools
import json
from google.cloud import mediatranslation as media
import pyaudio
from six.moves import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
SpeechEventType = media.StreamingTranslateSpeechResponse.SpeechEventType


class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk,configs,token):
        self._rate = rate
        self._chunk = chunk
        self.token=token
        
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self.seq_count=configs["seq_count"]

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type=None, value=None, traceback=None):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def exit(self):
        self.__exit__()

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

            yield b''.join(data)
    def zoom_post(self,text):
        post_params={
                'seq' : self.seq_count,
                'lang':"en-US"}
        headers={'Content-type': 'text/plain; charset=utf-8'}
        result=requests.post(self.token,params=post_params, data=text.encode('utf-8'),headers=headers)
        if result.status_code!=200:
            print("錯誤！傳送失敗！")
        self.seq_count=self.seq_count+1

def listen_print_loop(responses,stream):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.
    """
    translation = ''
    # source = ''
    for response in responses:
        # Once the transcription settles, the response contains the
        # END_OF_SINGLE_UTTERANCE event.
        if (response.speech_event_type ==
                SpeechEventType.END_OF_SINGLE_UTTERANCE) :

            stream.zoom_post(translation)
            # print(u'\nzoom translation: {0}'.format(translation))
            # print(u'recognition result: {0}'.format(source))
            return 0

        result = response.result
        translation = result.text_translation_result.translation
        # source = result.recognition_result

        print(u'\ntranslation: {0}'.format(translation))
        
        # print(u'recognition result: {0}'.format(source))


def do_translation_loop(configs,token):

    

    client = media.SpeechTranslationServiceClient()

    speech_config = media.TranslateSpeechConfig(
        audio_encoding='linear16',
        source_language_code=configs["source_lang"],
        target_language_code=configs["target_lang"])

    config = media.StreamingTranslateSpeechConfig(
        audio_config=speech_config, single_utterance=True)

    # The first request contains the configuration.
    # Note that audio_content is explicitly set to None.
    first_request = media.StreamingTranslateSpeechRequest(
        streaming_config=config, audio_content=None)

    with MicrophoneStream(RATE, CHUNK,configs,token) as stream:
        
        audio_generator = stream.generator()
        mic_requests = (media.StreamingTranslateSpeechRequest(
            audio_content=content,
            streaming_config=config)
            for content in audio_generator)

        requests = itertools.chain(iter([first_request]), mic_requests)

        responses = client.streaming_translate_speech(requests)

        # Print the translation responses as they arrive
        result = listen_print_loop(responses,stream)
        if result == 0:
            stream.exit()


def main():
    with open ("config.json") as config_file:
        configs=json.load(config_file)
    token=input("請輸入zoom API憑證：") 
    print('請開始說話（按下ctrl+c結束程式）：')
    while True:
    #     print()
    #     option = input('Press any key to translate or \'q\' to quit: ')

    #     if option.lower() == 'q':
    #         break

        do_translation_loop(configs,token)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('---------------------結束程式---------------------')
        sys.exit(0)
# [END media_translation_translate_from_mic]
