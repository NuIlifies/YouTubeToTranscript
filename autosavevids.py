import youtube_dl

import speech_recognition as sr

import os

from pydub import AudioSegment

from pydub.silence import split_on_silence

#from pocketsphinx import AudioFile, get_model_path, get_data_path

# https://www.youtube.com/watch?v=42OleX0HR4E
# stop looking up carykh smh


# get vid link and store to vid
vid = input("Paste video link: ")

# define ydl opts as parameters 4 downloading the video
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }],
}


# alternate 1, using local NN for speech to text
# def conv(title):
#   model_path = get_model_path()
#  data_path = get_data_path()

#   config = {
#       'verbose': False,
#       'audio_file': os.path.join(data_path, os.path.abspath(title)),
#       'buffer_size': 2048,
#       'no_search': False,
#       'full_utt': False,
#       'hmm': os.path.join(model_path, 'en-us'),
#       'lm': os.path.join(model_path, 'en-us.lm.bin'),
#   }
#   audio = AudioFile(**config)
#   for phrase in audio:
#       print(phrase)

# alternate 2, using google speech
def conv(title):
    song = AudioSegment.from_wav(title)
    fh = open("recognized.txt", "w+")

    chunks = split_on_silence(song,
                              min_silence_len=1000,
                              silence_thresh=-16, keep_silence=100, seek_step=1
                              )

    try:
        os.mkdir('audio_chunks')
    except(FileExistsError):
        pass

    os.chdir('audio_chunks')

    i = 0

    for chunk in chunks:
        chunk_silent = AudioSegment.silent(duration=10)
        audio_chunk = chunk_silent + chunk + chunk_silent
        print("saving chunk {0}.wav".format(i))

        audio_chunk.export("./chunk{0}.wav".format(i),
                           bitrate='192k', format="wav")
        filename = 'chunk' + str(i) + '.wav'

        print("Processing chunk " + str(i))
        file = filename
        r = sr.Recognizer()
        with sr.AudioFile(file) as source:
            r.adjust_for_ambient_noise(source)
            audio_listened = r.listen(source)

        try:
            rec = r.recognize_google(audio_listened)
            fh.write(rec + ". ")

        except sr.UnknownValueError:
            print("ERR in reading audio")

        except sr.RequestError as e:
            print("COULD NOT REQUEST RESULTS")

        i += 1

    os.chdir('..')



# ydl opts, ffmpeg paramters, being assigned to YoutubeDl as parameters, running as ydl
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # ydl download function inbuilt in the module, from input variable as string
    ydl.download([str(vid)])
    info_dict = ydl.extract_info(vid, download=False)
    i = info_dict.get('id', None)
    tit = i + ".wav"
    conv(tit)
