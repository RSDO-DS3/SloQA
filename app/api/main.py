########## IMPORTS ##########

from fastapi import FastAPI
from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer

########## PRELOADING MODELS ##########

print('Preloading models...')

model_names = [
    'bert-slo-squad_v2',
    'bert-tiny-slo-squad_v2',
    'roberta-base-slo-squad_v2',
    'xlm-roberta-base-slo-squad_v2',
    'sloberta-slo-squad_v2'
]

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

@app.get("/qa/")
async def qa(question: str, context: str, model_name: str):
    if model_name not in models:
        return {"status": "error", "message": "Model not found"}
    
    model = models[model_name]
    tokenizer = tokenizers[model_name]

    qa_pipeline = pipeline('question-answering', model=model.to('cpu'), tokenizer=tokenizer)

    result = qa_pipeline(question, context)

    return result