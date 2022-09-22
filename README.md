# Odgovarjanje na vprašanja

V tem repozitoriju se nahaja rezultat aktivnosti A3.4 Orodje za avtomatsko odgovarjanje na vprašanja, ki je nastalo v okviru projekta Razvoj slovenščine v digitalnem okolju.

---

## Project structure

- `app/` contains the web API for question answering
- `datasets/` contains the created datasets for question answering in the Slovenian language
- `models/` contains the fine-tuned models for question answering in the Slovenian language
- `train_eval/` contains the scripts for fine-tuning and evaluation

## Datasets

The datasets are organized as follows:

```
datasets/
└── SLO-SQuAD2.0-MT (machine translated SQuAD2.0)
|    └── data 
|    |    ├── squad2-slo-mt-dev.json (val set)
|    |    ├── squad2-slo-mt-train.json (train set)
|    └── translate.py (script for machine translation)
|
└── SLO-SuperGLUE
     ├── BoolQ
     ├── MultiRC
     └── ReCoRD
```

## Supported QA models

The built models are the following:

- bert-base-cased-squad2-SLO
- bert-base-multilingual-cased-squad2-SLO
- electra-base-squad2-SLO
- roberta-base-squad2-SLO
- sloberta-squad2-SLO
- xlm-roberta-base-squad2-SLO

Inspect `train_eval` folder for insight about training your own model.

### Model evaluation

| Model                                      | EM      | F1      |
|:-------                                    |:-------:|:-------:|
|bert-base-cased-squad2-SLO                  |55.12    |60.52    |
|bert-base-multilingual-cased-squad2-SLO     |61.37    |68.10    |
|electra-base-squad2-SLO                     |53.69    |60.85    |
|roberta-base-squad2-SLO                     |58.23    |64.62    |
|sloberta-squad2-SLO                         |67.10    |73.56    |
|xlm-roberta-base-squad2-SLO                 |62.52    |69.51    |


*Results were obtained by running the evaluation script on the `squad2-slo-mt-dev.json` file. Example for evaluating `bert-base-cased-squad2-SLO`:*

```
python fine_tune_HF.py \
     --do_eval \
     --model_name_or_path results/bert-base-cased-squad2-SLO \
     --validation_file squad2-slo-mt-dev.json \
     --output_dir results/bert-base-cased-squad2-SLO \
     --version_2_with_negative
```

## Deploy web API with docker

To deploy the web API with docker, first extract the models in .ZIP format to the `models` folder. Then copy the contents of folder `models` to `app/models`. The web API will serve all models in the folder by default, but you can modify `app/api/main.py` with the names of the specific models you want to serve.

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
     - `bert-base-cased-squad2-SLO`
     - `bert-base-multilingual-cased-squad2-SLO`
     - `electra-base-squad2-SLO`
     - `roberta-base-squad2-SLO`
     - `sloberta-squad2-SLO`
     - `xlm-roberta-base-squad2-SLO`

*The info on parameters of the question answering endpoint can be retrieved using a GET endpoint at `http://localhost:8008/params`.*

## Live demo

The WebAPI can be tested live at http://164.8.252.73:8008/docs



---

> Operacijo Razvoj slovenščine v digitalnem okolju sofinancirata Republika Slovenija in Evropska unija iz Evropskega sklada za regionalni razvoj. Operacija se izvaja v okviru Operativnega programa za izvajanje evropske kohezijske politike v obdobju 2014-2020.

![](Logo_EKP_sklad_za_regionalni_razvoj_SLO_slogan.jpg)
