import keyboard
import speech_recognition as sr

def record_voice():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print("Speak something...")
        audio = recognizer.listen(source)

    try:
        print("Transcribing...")
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"Transcription: {text}")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError:
        print("Error connecting to Google API.")

def on_space_pressed(e):
    if e.event_type == keyboard.KEY_DOWN:
        record_voice()

keyboard.on_press_key("space", on_space_pressed)

print("Press the space bar to record your voice. Press 'Esc' to stop the program.")

keyboard.wait("esc")  # Wait for 'Esc' key to exit the program
