import google.generativeai as genai

genai.configure(api_key="AIzaSyCN5Fgv95lXgBItWIeW15xZTg2ie-PUXz0")

models = genai.list_models()

for model in models:
    print(model.name)
