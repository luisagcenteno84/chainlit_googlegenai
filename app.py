import chainlit as cl
import google.generativeai as genai

from google.cloud import storage
import PIL 
import requests
import io 
from google.generativeai.types import HarmCategory,HarmBlockThreshold
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# Initialize the Generative AI model
PROJECT_ID="solid-sun-418711"
LOCATION="us-west1"

model = genai.GenerativeModel('gemini-pro')
model_vision = genai.GenerativeModel('models/gemini-pro-vision') 
model_image = ImageGenerationModel.from_pretrained('imagegeneration@006')


@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")



@cl.on_message
async def on_message(message: cl.Message):

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

    elif(message.content.startswith("/imagine")):
        prompt = message.content

        response = model_image.generate_images(prompt=prompt)        

        file_name = prompt.replace("/imagine ", "")
        file_name = file_name.replace(" ", "_")
        file_name = file_name.replace(",", "")
        file_name = file_name.replace(".", "")
        file_name = file_name.replace("\n", "")
        file_name = file_name.replace("\t", "")
        file_name = file_name.lower()

        if(len(file_name) > 20):
            file_name = file_name[0:20] 

        file_name = file_name + ".png"

        storage_client = storage.Client()
        bucket = storage_client.bucket('chainlit-genai-vision-bucket')

        blob = bucket.blob("agenerated/"+file_name)

        blob.upload_from_string(response.images[0]._image_bytes, content_type="image/png")

        blob_path = "https://storage.cloud.google.com/chainlit-genai-vision-bucket/agenerated/"+file_name
        
    else:
        response = model.generate_content(message.content, safety_settings=safety_settings) 

    if(isinstance(response,vertexai.preview.vision_models.ImageGenerationResponse)):
        answer = cl.Message(content="", elements=[cl.Image(url=blob_path, name=file_name, display="inline")])
   
    elif len(response.candidates) > 0:
        answer = cl.Message(content=response.candidates[0].content.parts[0].text)
    elif len(response.parts) > 0:
        answer = cl.Message(content=response.parts[0].text)
    else: 
        answer = cl.Message(content=response) 
    

    await answer.send()
