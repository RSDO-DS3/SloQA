########## IMPORTS ##########

from fastapi import FastAPI
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer
import os
from pydantic import BaseModel

########## INPUT OBJECT ##########
class InputJSON(BaseModel):
    question: str
    context: str
    model_name: str

########## PRELOADING MODELS ##########

print('Preloading models...')

model_folder = '../models/'

# read "models" folder for models to serve
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

@app.post("/qa/")
async def qa(input: InputJSON):
    question = input.question
    context = input.context
    model_name = input.model_name

    if model_name not in models:
        return {"status": "error", "message": "Model not available"}
    
    model = models[model_name]
    tokenizer = tokenizers[model_name]

    qa_pipeline = pipeline('question-answering', model=model.to('cpu'), tokenizer=tokenizer)

    result = qa_pipeline(question=question, context=context, top_k=3)

    return result