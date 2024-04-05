import google.generativeai as genai

for model in genai.list_models():
    print(model.name + " - " + model.display_name + " - " + ', '.join(method for method in model.supported_generation_methods))

