########## IMPORTS ##########

from fastapi import FastAPI
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import os
########## PRELOADING MODELS ##########

print('Preloading models...')

model_folder = '../models/'

# read models folder for models to serve
model_names = [name for name in os.listdir(model_folder) if os.path.isdir(os.path.join(model_folder, name))]

# or manually define the models to serve
#model_names = [
#   'sloberta-squad2-SLO',
#   'xlm-roberta-base-squad2-SLO'
#]

models = {}
tokenizers = {}

for model_name in model_names:
    print(f'Loading {model_name}...')
    model = AutoModelForQuestionAnswering.from_pretrained(f'../models/{model_name}') 
    tokenizer = AutoTokenizer.from_pretrained(f'../models/{model_name}') 

    models[model_name] = model
    tokenizers[model_name] = tokenizer

print('Models loaded!')

########## API ##########

app = FastAPI()

@app.get("/")
async def status():
    return {"status": "active"}

@app.get("/params")
async def params():
    names = ", ".join(model_names)
    return {
        "question": "string: string with text representing the question",
        "context": "string: string with text representing the context",
        "model_name": "string: string representing the model name; can be one of: " + names
    }

@app.get("/qa/")
async def qa(question: str, context: str, model_name: str):
    if model_name not in models:
        return {"status": "error", "message": "Model not found"}
    
    model = models[model_name]
    tokenizer = tokenizers[model_name]

    qa_pipeline = pipeline('question-answering', model=model.to('cpu'), tokenizer=tokenizer)

    result = qa_pipeline(question, context)

    return result