# Odgovarjanje na vprašanja

V tem repozitoriju se nahaja rezultat aktivnosti A3.4 Orodje za avtomatsko odgovarjanje na vprašanja, ki je nastalo v okviru projekta Razvoj slovenščine v digitalnem okolju.

---

## Project structure

- `app/` contains the web API for question answering
- `datasets/` contains the created datasets for question answering in the Slovenian language
- `demo/` contains a Jupyter Notebook for quick demonstrations of the question answering models
- `models/` contains the fine-tuned models for question answering in the Slovenian language

## Datasets

The datasets are organized as follows:

```
datasets/
└── SLO-SQuAD2.0-MT (machine translated SQuAD2.0)
|    └── data 
|    |    ├── slo-squad2-mt-train (train set)
|    |    ├── slo-squad2-mt-val (val set)
|    |    ├── errors-train.csv (set of erroneous questions from the train set)
|    |    ├── errors-val.csv (set of erroneous questions from the val set)
|    ├── translate.py (script for machine translation)
|    └── train-qa.py (script for model fine-tuning)
|
└── SLO-SuperGLUE
     ├── BoolQ
     ├── MultiRC
     └── ReCoRD
```

## Question answering demo (Jupyter Notebook)

For quick demonstrations, a Jupyter Notebook is available to demonstrate the use of models for question answering in the Slovenian language. The demo contains two text paragraphs with a few questions to try out.

## Supported QA models

The built models are the following:

- BERT-base
- BERT-tiny
- RoBERTa-base
- XLM-RoBERTa-base
- SloBERTa

Inspect `train-qa.py` for insight about training your own model.

## Deploy web API with docker

To deploy the web API with docker, first copy the contents of folder `models` to `app/models`. Modify `app/api/main.py` with the names of the models you want to serve.

To build the docker image run:

```
docker build -t rsdo-qa-api .
docker run -d --name rsdo-qa-docker -p 8008:80 rsdo-qa-api
```
Service starts when the logger outputs: `INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)`

Test the web api by navigating to: `http://localhost:8008/`. The result should be:

```
{'status': 'active'}
```

## Web API

The web API is supported by FastAPI/uvicorn.

 After starting up the API, the OpenAPI/Swagger documentation will become accessible at `http://localhost:8008/docs` and `http://localhost:8008/openapi.json`. Alternatively, the redoc documentation will be accessible at `http://localhost:8008/redoc`.

 The service has a GET endpoint at `http://localhost:8008/qa`. The endpoint requires three parameters:

 - String `question`    Text containing the question.
 - String `context`     Text containing the context (usually a paragraph of text)
 - String `model_name`  The name of the model. Currently supported options are:
    - `bert-slo-squad_v2`
    - `bert-tiny-slo-squad_v2`
    - `roberta-base-slo-squad_v2`
    - `xlm-roberta-base-slo-squad_v2`
    - `sloberta-slo-squad_v2`

---

> Operacijo Razvoj slovenščine v digitalnem okolju sofinancirata Republika Slovenija in Evropska unija iz Evropskega sklada za regionalni razvoj. Operacija se izvaja v okviru Operativnega programa za izvajanje evropske kohezijske politike v obdobju 2014-2020.

![](Logo_EKP_sklad_za_regionalni_razvoj_SLO_slogan.jpg)
