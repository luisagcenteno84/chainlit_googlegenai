from google.cloud import texttospeech


client = texttospeech.TextToSpeechClient()
voices = client.list_voices()

for voice in voices.voices:
    print("Name:["+ voice.name+ "] ")
    for code in voice.language_codes:
        print("Language code:["+ code+ "] ")