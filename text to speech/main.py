from gtts import gTTS

text = "Hello! this is kamali, Nice to meet you.."

tts = gTTS(text= text, lang = "en")

tts.save("sample_speech.mp3")

print("speech saved as sample_speech.mp3")