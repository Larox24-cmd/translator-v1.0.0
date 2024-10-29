# Import necessary libraries
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import os
import tkinter as tk
from tkinter import messagebox
import threading

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()
audio_data = None  # Global variable to hold audio data

# ASU Theme Colors
MAROON = "#8C1D40"
GOLD = "#FFC72C"
FONT = ("Helvetica", 24, "bold")

# Mapping of selected languages to their Google Translate API codes
language_mapping = {
    "Spanish": "es",
    "Irish": "ga",
    "French": "fr",
    "Vietnamese": "vi",
    "Tagalog": "tl",
    "Arabic": "ar",
    "Chinese": "zh-cn",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te"
}

# Global variable for selected language code and main app reference
language_code = None
main_app = None  # To hold the reference to the main application window
listening_thread = None  # To keep track of the listening thread

# Splash screen function
def show_splash():
    splash = tk.Toplevel()
    splash.title("EGR 104")
    splash.attributes("-fullscreen", True)
    splash.configure(bg=MAROON)
    
    label = tk.Label(splash, text="EGR 104", font=("Helvetica", 48, "bold"), fg=GOLD, bg=MAROON)
    label.pack(expand=True)
    
    loading_label = tk.Label(splash, text="Loading...", font=FONT, fg=GOLD, bg=MAROON)
    loading_label.pack(pady=10)
    
    # Show splash screen for 3 seconds, then open the main window
    splash.after(3000, lambda: (splash.destroy(), show_main_app()))

# Function to set language and open countdown window
def set_language_and_proceed(code):
    global language_code
    language_code = code  # Set the selected language code
    main_app.destroy()  # Close the main window
    show_countdown_window()

# Countdown window before starting translation
def show_countdown_window():
    countdown_win = tk.Toplevel()
    countdown_win.title("Get Ready")
    countdown_win.attributes("-fullscreen", True)
    countdown_win.configure(bg=MAROON)

    countdown_label = tk.Label(countdown_win, text="", font=("Helvetica", 72, "bold"), fg=GOLD, bg=MAROON)
    countdown_label.pack(expand=True)

    # Translate button to manually end countdown and proceed
    translate_button = tk.Button(countdown_win, text="Translate", font=FONT, bg=GOLD, fg=MAROON,
                                 command=lambda: stop_listening_and_translate(countdown_win))
    translate_button.pack(pady=20)

    def countdown(count):
        if count > 0:
            countdown_label.config(text=f"{count}")
            countdown_win.after(1000, countdown, count - 1)
        else:
            countdown_label.config(text="Start Speaking...")
            countdown_win.update()
            start_listening(countdown_win)

    countdown(3)  # Start countdown from 3

# Start listening on a separate thread
def start_listening(countdown_win):
    global listening_thread
    listening_thread = threading.Thread(target=listen_for_audio, args=(countdown_win,))
    listening_thread.start()

# Function to listen to audio
def listen_for_audio(countdown_win):
    global audio_data
    with sr.Microphone() as source:
        print("Listening for speech...")
        audio_data = recognizer.listen(source)

    # After audio is recorded, proceed to translation
    translate_audio(countdown_win)

# Stop listening and proceed to translation
def stop_listening_and_translate(countdown_win):
    global listening_thread, audio_data
    if listening_thread and listening_thread.is_alive():
        # End listening and use the recorded audio, if available, otherwise skip listening
        listening_thread.join(timeout=1)  # Gracefully attempt to end thread
        if not audio_data:
            messagebox.showinfo("Notice", "No audio detected. Proceeding without audio.")
            countdown_win.destroy()
        else:
            translate_audio(countdown_win)

# Main application window with language buttons in grid layout
def show_main_app():
    global main_app
    main_app = tk.Tk()
    main_app.title("ASU Voice Translator")
    main_app.attributes("-fullscreen", True)
    main_app.configure(bg=MAROON)

    title_label = tk.Label(main_app, text="ASU Voice Translator", font=("Helvetica", 48, "bold"), fg=GOLD, bg=MAROON)
    title_label.pack(pady=10)

    lang_label = tk.Label(main_app, text="Select a Language:", font=FONT, fg=GOLD, bg=MAROON)
    lang_label.pack(pady=10)

    # Frame for language buttons
    button_frame = tk.Frame(main_app, bg=MAROON)
    button_frame.pack(pady=20)

    # Arrange language buttons in a grid (2-3 rows)
    row, col = 0, 0
    for language, code in language_mapping.items():
        btn = tk.Button(button_frame, text=language, font=FONT, bg=GOLD, fg=MAROON,
                        command=lambda c=code: set_language_and_proceed(c))
        btn.grid(row=row, column=col, padx=20, pady=10, ipadx=10, ipady=5)
        col += 1
        if col > 2:  # Change row after 3 columns
            col = 0
            row += 1

    main_app.mainloop()

# Function to display the translation result in a fullscreen window
def show_translation(translation_text):
    translation_win = tk.Toplevel()
    translation_win.title("Translation")
    translation_win.attributes("-fullscreen", True)
    translation_win.configure(bg=MAROON)

    translation_label = tk.Label(translation_win, text="Translated Text:", font=("Helvetica", 48, "bold"), fg=GOLD, bg=MAROON)
    translation_label.pack(pady=20)

    result_label = tk.Label(translation_win, text=translation_text, font=("Helvetica", 36), fg=GOLD, bg=MAROON, wraplength=1000)
    result_label.pack(expand=True)

    close_button = tk.Button(translation_win, text="Close", font=FONT, bg=GOLD, fg=MAROON, command=translation_win.destroy)
    close_button.pack(pady=20)

# Function to perform translation and speech conversion
def translate_audio(countdown_win):
    global audio_data, language_code
    if not language_code:
        messagebox.showwarning("Language Selection", "Please choose a language first.")
        return
    countdown_win.destroy()

    if audio_data is not None:
        try:
            text = recognizer.recognize_google(audio_data)
            print("You said:", text)
            translation = translator.translate(text, dest=language_code)
            print("Translated:", translation.text)
            show_translation(translation.text)

            tts = gTTS(translation.text, lang=language_code)
            tts.save("output.mp3")
            os.system("start output.mp3") if os.name == 'nt' else os.system("open output.mp3")

        except ValueError:
            messagebox.showerror("Error", "Error in translation. Please try again.")
    else:
        messagebox.showinfo("Notice", "No audio detected. Please try again.")

def retry():
    global language_code, audio_data
    language_code = None
    audio_data = None
    messagebox.showinfo("Reset", "Language selection has been reset.")

# Start the splash screen
root = tk.Tk()
root.withdraw()  # Hide the main root window while the splash screen shows
show_splash()
root.mainloop()
