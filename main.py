import youtube_dl

import speech_recognition as sr

import os

from pydub import AudioSegment

from pydub.utils import make_chunks

#from pocketsphinx import AudioFile, get_model_path, get_data_path


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


def conv(title):
    s = AudioSegment.from_file(title, "wav")
    fh = open("recognized.txt", "w+")
    chunk_length = 10000
    chunks = make_chunks(s, chunk_length)
    try: 
        os.mkdir('audio_chunks')
    except(FileExistsError):
        pass
    
    os.chdir('audio_chunks')
    i = 0
    er = 0
    for chunk in chunks:
        chunk_name = "chunk{0}.wav".format(i)
        print("exporting ", chunk_name)
        chunk.export(chunk_name, format="wav")
        filename = chunk_name
        
        r = sr.Recognizer()
 

        with sr.AudioFile(filename) as source:
            audio_listened = r.listen(source)
        try:
            rec = r.recognize_google(audio_listened)
            if rec[len(rec) - 1] != " ":
                rec = rec + " "
            fh.write(rec)

        except sr.UnknownValueError:
            print("Couldn't read data for " + chunk_name + ". Inaudible?")   
            os.remove(chunk_name)
            er += 1
        i += 1


    os.chdir('..')
    print('Successfully completed operation with ' + str(er) + ' exception(s)')
    os.remove(title)





# ydl opts, ffmpeg paramters, being assigned to YoutubeDl as parameters, running as ydl
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    # ydl download function inbuilt in the module, from input variable as string
    ydl.download([str(vid)])
    info_dict = ydl.extract_info(vid, download=False)
    i = info_dict.get('id', None)
    tit = i + ".wav"
    conv(tit)
