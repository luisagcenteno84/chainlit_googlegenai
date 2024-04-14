import chainlit as cl
import google.generativeai as genai

from google.cloud import storage
import PIL 
import requests
import io 
from google.generativeai.types import HarmCategory,HarmBlockThreshold
# Initialize the Generative AI model

model = genai.GenerativeModel('gemini-pro')
model_vision = genai.GenerativeModel('models/gemini-pro-vision') 



@cl.on_chat_start
def on_chat_start():

    print("A new chat session has started!")



@cl.on_message
async def on_message(message: cl.Message):
    #print(len(message.elements))

    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE}

    if(len(message.elements) > 0):
        storage_client = storage.Client()
        bucket = storage_client.bucket('chainlit-genai-vision-bucket')
        blob = bucket.blob(message.elements[0].name)

        blob.upload_from_filename(message.elements[0].path)

        blob_as_string = blob.download_as_string()

        bytes = io.BytesIO(blob_as_string)
        img = PIL.Image.open(bytes)
        response = model_vision.generate_content([message.content,img],safety_settings=safety_settings)
    else:
        response = model.generate_content(message.content, safety_settings=safety_settings) 
    print(response)




    if len(response.candidates) > 0:
        print("Got Candidates")
        for candidate in response.candidates:
            print("Candidate:")
            print(candidate)
            answer = response.candidates[0].content

    if len(response.parts) > 0:
        print("Got Parts")
        for part in response.parts:
            print("Part")
            print(part)
            answer = response.parts[0].text
    else: 
        answer = response 
    

    await cl.Message(answer).send()
