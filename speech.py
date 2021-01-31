# importing the module
import speech_recognition as sr


# define the recognizer
r = sr.Recognizer()


# define the audio file
audio_file = sr.AudioFile('history.wav')


# speech recognition
with audio_file as source: 
   r.adjust_for_ambient_noise(source) 
   audio = r.record(source)
result = r.recognize_google(audio)


# exporting the result 
with open('test1.txt', mode ='w') as file: 
   file.write("Recognized text:\n") 
   file.write(result) 
   print("ready!")
