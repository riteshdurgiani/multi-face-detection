# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 19:52:16 2020

@author: Priyanka
"""

import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
from apscheduler.schedulers.background import BackgroundScheduler
import glob


window = tk.Tk()
window.title("Face_Recogniser")

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'
window.configure(background='#F9B868')
                 
message = tk.Label(window, text="MULTI FACE DETECTION",width=70  ,height=3  ,fg="black"  ,bg="#F5E5FC" ,font=('times', 30, ' bold ') ) 
message.place(x=0, y=0)

lbl = tk.Label(window, text="Enter ID",width=18  ,height=2  ,fg="black"  ,bg="#C0FF96" ,font=('times', 15, ' bold ') ) 
lbl.place(x=350, y=300)

txt = tk.Entry(window,width=20  ,bg="#C0FF96" ,fg="black",font=('times', 15, ' bold '))
txt.place(x=600, y=315)

lbl2 = tk.Label(window, text="Enter Name",width=18  ,fg="black"  ,bg="#C0FF96"    ,height=2 ,font=('times', 15, ' bold ')) 
lbl2.place(x=350, y=400)

txt2 = tk.Entry(window,width=20 ,bg="#C0FF96"  ,fg="black",font=('times', 15, ' bold ')  )
txt2.place(x=600, y=415)

lbl3 = tk.Label(window, text="Notification : ",width=18  ,fg="black"  ,bg="#C0FF96"  ,height=2 ,font=('times', 15, ' bold underline ')) 
lbl3.place(x=350, y=500)

message = tk.Label(window, text="" ,bg="#C0FF96"  ,fg="black"  ,width=30  ,height=2, activebackground = "grey" ,font=('times', 15, ' bold ')) 
message.place(x=600, y=500)

lbl3 = tk.Label(window, text="Attendance : ",width=18  ,fg="black"  ,bg="#C0FF96"  ,height=2 ,font=('times', 15, ' bold  underline')) 
lbl3.place(x=350, y=600)


message2 = tk.Label(window, text="" ,fg="black"   ,bg="#C0FF96",activeforeground = "grey",width=30  ,height=4  ,font=('times', 15, ' bold ')) 
message2.place(x=600, y=600)
 

lbl4 = tk.Label(window, text="Scheduling time in secs",width=18  ,height=2  ,fg="black"  ,bg="#C0FF96" ,font=('times', 15, ' bold ') ) 
lbl4.place(x=350, y=200)

txt1 = tk.Entry(window,width=20  ,bg="#C0FF96" ,fg="black",font=('times', 15, ' bold '))
txt1.place(x=600, y=215)

def clear():
    txt.delete(0, 'end')    
    res = ""
    message.configure(text= res)

def clear2():
    txt2.delete(0, 'end')    
    res = ""
    message.configure(text= res)    
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
 
def TakeImages():        
    Id=(txt.get())
    name=(txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while(True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
                #incrementing sample number 
                sampleNum=sampleNum+1
                #saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                #display the frame
                cv2.imshow('frame',img)
            #wait for 100 miliseconds 
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 120
            elif sampleNum>120:
                break
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for ID : " + Id +" Name : "+ name
        row = [Id , name]
        with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text= res)
    else:
        if(is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text= res)
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("TrainingImageLabel\Trainner.yml")
    res = "Image Trained"#+",".join(str(f) for f in Id)
    message.configure(text= res)

def getImagesAndLabels(path):
   
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    faces=[]
    Ids=[]
    for imagePath in imagePaths:
        pilImage=Image.open(imagePath).convert('L')
        imageNp=np.array(pilImage,'uint8')
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("TrainingImageLabel\Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)    
    t=60
    while t>0:
        t -= 1
        time.sleep(1)
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 70):
                ts = time.time()      
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['Id'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                
            else:
                Id='Unknown'                
                tt=str(Id)  
            if(conf > 50):
                noOfFile=len(os.listdir("ImagesUnknown"))+1
                #cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im) 
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="Attendance\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    #print(attendance)
    res=attendance
    message2.configure(text= res)

def startSchedule():
    i=0
    scheduleImages(i)

def quitSchedule():
    i=1
    scheduleImages(i)

sched = BackgroundScheduler()
def startScheduler():
    sched.start()
    
def stopScheduler():
    sched.shutdown()
    
def scheduleImages(i):
    if(i==0):
        print("In scheduling")
        if(sched.state==0):
            startScheduler()
        t=int(txt1.get())
        sched.add_job(TrackImages,'interval',seconds=t,id="attendance")
    elif(i==1):
        sched.remove_job("attendance")

def quitApp():
    try:
        stopScheduler()
    finally:
        window.destroy()
    
def markFinalAttendance():

    path=r'C:\Users\Manoj Ajwani\Desktop\MAJOR PROJECT\Face-Recognition-Based-Attendance-System-master\Attendance'
    all_files = glob.glob(os.path.join(path,"*.csv"))

    big_dataframe=[]
    collist=["id","date","name","time"]
    final_list=[]
    fl=[]


    for file in all_files:
        df=pd.read_csv(file)
        big_dataframe.append(df)

    for df in big_dataframe:
        vals=df.iloc[:,0].values
        for val in vals:
            final_list.append(val)

    for v in final_list:
        if final_list.count(v)>2:
            fl.append(v)
        else:
            continue

    final_attendance=set(fl)
    dvf=pd.DataFrame(final_attendance)
    writer=pd.ExcelWriter('final.xlsx',engine='xlsxwriter')
    dvf.to_excel(writer,sheet_name="FinalAttendance")
    writer.save()


  
clearButton = tk.Button(window, text="Clear", command=clear2  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2 ,activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
clearButton.place(x=834, y=400)
clearButton2 = tk.Button(window, text="Clear", command=clear  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
clearButton2.place(x=834, y=300)    
takeImg = tk.Button(window, text="Take Images", command=TakeImages  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
takeImg.place(x=1050, y=300)
trainImg = tk.Button(window, text="Train Images", command=TrainImages  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
trainImg.place(x=1050, y=400)
trackImg = tk.Button(window, text="Track Images", command=TrackImages  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
trackImg.place(x=1050, y=500)
quitWindow = tk.Button(window, text="Quit", command=  quitApp ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
quitWindow.place(x=1050, y=600)

scheduleButton = tk.Button(window, text="Start Scheduling", command=startSchedule  ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2 ,activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
scheduleButton.place(x=834, y=200)
scheduleButton2 = tk.Button(window, text="Stop Scheduling", command=quitSchedule ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
scheduleButton2.place(x=1050, y=200)    


final_attendance = tk.Button(window, text="Final Attendance", command=markFinalAttendance ,fg="black"  ,bg="#96E1F2"  ,width=15  ,height=2, activebackground = "#96E1F2" ,font=('times', 15, ' bold '))
final_attendance.place(x=700, y=725)    


 
window.mainloop()