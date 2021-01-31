import tkinter
from tkinter import *
import tkinter.messagebox as messagebox
from tkinter import filedialog
import request as rq

file_name = ""
top = tkinter.Tk()
def UploadAction(event = None):
    filename = filedialog.askopenfilename()
    filename = filename.split("/")[-1]
    print('Selected:', filename)
    script = rq.google_transcribe(filename)
    f = open("output.txt", "w")
    f.seek(0)
    f.write(script)
    f.close()
    whole, output = rq.generate_summary("./output.txt")
    l = Label(top, text = "Top 3 Ranked Sentence(s)\n\n"+output+"\n\nWhole Text: \n"+whole, wraplength=600, justify="center", bg="pink") 
    l.config(font = ("Courier", 12)) 
    l.pack()   
l = Label(top,text = "Please Upload your Wav File Here to Get a Summary", bg="pink") 
l.config(font = ("Courier", 12)) 
l.pack()
B = tkinter.Button(top, text = "Upload Here", command = UploadAction, bg="pink")
B.pack()
top.mainloop()

