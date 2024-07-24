import cv2
import numpy as np
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import winsound
import time
import webbrowser
import os

# Initialize the recognizer and the TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Paths to YOLO files
weights_path = "yolov3.weights"  # Ensure the file is in the current directory or specify the correct path
config_path = "yolov3.cfg"       # Ensure the file is in the current directory or specify the correct path
names_path = "coco.names"        # Ensure the file is in the current directory or specify the correct path

# Load YOLO
net = cv2.dnn.readNet(weights_path, config_path)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

# Load class names
with open(names_path, "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Define colors for each class
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# Function to list available voices
def list_voices():
    voices = tts_engine.getProperty('voices')
    for idx, voice in enumerate(voices):
        print(f"Voice {idx}: {voice.name}")
    return voices

# Function to speak a given text
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to get the current time in 12-hour format
def get_time():
    now = datetime.now()
    current_time = now.strftime("%I:%M:%S %p")
    return current_time

# Function to open Gmail
def open_gmail():
    webbrowser.open("https://mail.google.com")

# Function to open Microsoft Edge
def open_edge():
    os.startfile("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")

# Function to open Google Chrome
def open_chrome():
    os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

# Function to open Desktop
def open_desktop():
    os.startfile(os.path.join(os.path.expanduser("~"), "Desktop"))

# Function to open Notepad
def open_notepad():
    os.startfile("notepad.exe")

# Function to open Recycle Bin
def open_recycle_bin():
    os.system("start shell:RecycleBinFolder")

# Function to open ChatGPT (assuming web version)
def open_chatgpt():
    webbrowser.open("https://chat.openai.com")

# Function to open WhatsApp Web
def open_whatsapp():
    webbrowser.open("https://web.whatsapp.com")

# Function to open YouTube
def open_youtube():
    webbrowser.open("https://youtube.com")

# Function to open YouTube Music
def open_youtube_music():
    webbrowser.open("https://music.youtube.com")

# Function to open Google Chrome with a search query
def search_on_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)

# Function to open Instagram Web
def open_instagram():
    webbrowser.open("https://instagram.com")

# Function to recognize speech with optional prompt beep
def recognize_speech(prompt=False):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        if prompt:
            winsound.Beep(1000, 50)  # Shortened beep before listening
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your network connection.")
            return ""

# Function to perform object detection
def detect_objects(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                w = int(obj[2] * width)
                h = int(obj[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply Non-Maximum Suppression (NMS)
    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

    detected_objects = []
    if len(indices) > 0:
        indices = indices.flatten()
        for i in indices:
            detected_objects.append(classes[class_ids[i]])

    return detected_objects

# Main loop focusing on wake word detection
def main():
    while True:
        print("Waiting for wake word and command...")
        text = recognize_speech()
        if "fiona" in text:
            print("Wake word detected")
            winsound.Beep(1000, 50)  # Shortened beep to indicate wake word detected
            
            # Strip the wake word from the command
            command = text.replace("fiona", "").strip()

            # List of phrases for each command
            time_phrases = ["time", "what's the time", "tell me the time"]
            gmail_phrases = ["open gmail", "open my gmail", "will you open gmail for me"]
            edge_phrases = ["open microsoft edge", "open edge", "will you open microsoft edge for me"]
            chrome_phrases = ["open google chrome", "open chrome", "will you open google chrome for me"]
            desktop_phrases = ["open my desktop", "show my desktop", "will you open the desktop"]
            notepad_phrases = ["open notepad", "open a notepad", "will you open notepad for me"]
            recycle_bin_phrases = ["open recycle bin", "open my recycle bin", "will you open the recycle bin"]
            chatgpt_phrases = ["open chatgpt", "open chat gpt", "will you open chatgpt for me"]
            whatsapp_phrases = ["open whatsapp", "open my whatsapp", "will you open whatsapp for me"]
            youtube_phrases = ["open youtube", "open my youtube", "will you open youtube for me"]
            youtube_music_phrases = ["open youtube music", "open my youtube music", "will you open youtube music for me"]
            search_phrases = ["search", "search for", "look up", "look for"]
            object_detection_phrases = ["what's in my hand", "what am i"]
            instagram_phrases = ["open instagram", "open my instagram", "will you open instagram for me"]

            # Check command against all phrases
            if not command:  # No command given
                speak("Yes.")
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in time_phrases):
                current_time = get_time()
                speak(f"The current time is {current_time}")
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in gmail_phrases):
                speak("Opening Gmail.")
                open_gmail()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in edge_phrases):
                speak("Opening Microsoft Edge.")
                open_edge()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in chrome_phrases):
                speak("Opening Google Chrome.")
                open_chrome()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in desktop_phrases):
                speak("Opening Desktop.")
                open_desktop()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in notepad_phrases):
                speak("Opening Notepad.")
                open_notepad()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in recycle_bin_phrases):
                speak("Opening Recycle Bin.")
                open_recycle_bin()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in chatgpt_phrases):
                speak("Opening ChatGPT.")
                open_chatgpt()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in whatsapp_phrases):
                speak("Opening WhatsApp.")
                open_whatsapp()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in instagram_phrases):
                speak("Opening Instagram.")
                open_instagram()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in youtube_phrases):
                speak("Opening YouTube.")
                open_youtube()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in youtube_music_phrases):
                speak("Opening YouTube Music.")
                open_youtube_music()
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in search_phrases):
                # Extract the search query
                for phrase in search_phrases:
                    if phrase in command:
                        query = command.replace(phrase, "").strip()
                        break
                if query:
                    speak(f"Searching for {query} .")
                    search_on_google(query)
                    time.sleep(0.5)  # Half-second delay after speaking
                    winsound.Beep(1000, 30)  # Shortened double beep after processing
                    winsound.Beep(1000, 30)
                else:
                    speak("I didn't catch that. Can you please repeat?")
                    time.sleep(0.5)  # Half-second delay after speaking
                    winsound.Beep(1000, 30)  # Shortened double beep after processing
                    winsound.Beep(1000, 30)
            elif any(phrase in command for phrase in object_detection_phrases):
                # Perform object detection
                speak("Let me see.")
                video_capture = cv2.VideoCapture(0)
                ret, frame = video_capture.read()
                video_capture.release()
                
                # Perform object detection on the captured frame
                detected_objects = detect_objects(frame)
                if detected_objects:
                    speak(f"I see {', '.join(detected_objects)} in your hand.")
                else:
                    speak("I couldn't detect any object in your hand.")
                
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)
            else:
                speak("I didn't catch that. Can you please repeat?")
                time.sleep(0.5)  # Half-second delay after speaking
                winsound.Beep(1000, 30)  # Shortened double beep after processing
                winsound.Beep(1000, 30)

if __name__ == "__main__":
    # List available voices for user to choose
    voices = list_voices()
    
    # Set the desired voice
    choice = int(input("Choose a voice (by number): "))
    tts_engine.setProperty('voice', voices[choice].id)
    
    # Start the main loop
    main()
