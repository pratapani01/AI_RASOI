import speech_recognition as sr
import time

def transcribe_audio():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎙️ Please start speaking now...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            # Start recording and limit to 10 seconds
            audio = recognizer.listen(source, timeout=10)  # Timeout after 10 seconds of silence

            print("🎙️ Transcribing...")
            text = recognizer.recognize_google(audio)
            print("✅ Transcription:", text)
            return text
        except sr.WaitTimeoutError:
            return "No speech detected in the given time. Please try again."
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Could not request results; check your internet connection."
