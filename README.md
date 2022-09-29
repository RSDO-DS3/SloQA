# Odgovarjanje na vprašanja

V tem repozitoriju se nahaja rezultat aktivnosti A3.4 Orodje za avtomatsko odgovarjanje na vprašanja, ki je nastalo v okviru projekta Razvoj slovenščine v digitalnem okolju.

---

## Project structure

- `app/` contains the web API for question answering
- `datasets/` contains the created datasets for question answering in the Slovenian language
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

Currently supported models ([download link](https://univerzamb-my.sharepoint.com/personal/mladen_borovic_um_si/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fmladen%5Fborovic%5Fum%5Fsi%2FDocuments%2FResearch%2FRSDO%2FR3%2E4%20QA%2Fmodels&ga=1)) are the following:

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
docker run -d --name rsdo-qa-docker -p 8008:80 --restart always rsdo-qa-api
```
Service starts when the logger outputs: `INFO:     Uvicorn running on http://0.0.0.0:80 (Press CTRL+C to quit)`

Test the web api by navigating to: `http://localhost:8008/`. The result should be:

```
{'status': 'active'}
```

## Web API

The web API is supported by FastAPI/uvicorn.

 After starting up the API, the OpenAPI/Swagger documentation will become accessible at `http://localhost:8008/docs` and `http://localhost:8008/openapi.json`. Alternatively, the redoc documentation will be accessible at `http://localhost:8008/redoc`.

 The service has a POST endpoint at `http://localhost:8008/qa`. The endpoint requires a JSON object as input in this format:

```
{
     "question": [text containing the question],
     "context": [text containing the context (usually a paragraph of text)],
     "model_name": [the name of the model]
}
```
Refer to section [Supported models](#supported-qa-models) for currently supported models.

#### Example

Example input with model *sloberta-squad2-SLO*:
```
curl -X 'POST' \
  'http://localhost:8008/qa/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Katera stran glede diskriminacije je začela delovati?",
  "context": "V sklopu Evropskega leta enakih možnosti za vse je začela delovati spletna stran www.protidiskriminaciji.si, s čimer želijo ustvarjalci in posredno tudi Evropska unija ljudi opozoriti na različne vrste diskriminacije, saj zakonodaja na nacionalni in ravni Evropske unije ne zadostuje za njeno preprečevanje. Kot poudarjajo v Studiu 3S, ki je nosilec projekta omenjene spletne strani, se morajo premiki zgoditi v svetu posameznikov, o diskriminaciji pa je treba pisati in se o njej izobraževati. Kljub strogim delovno-pravnim zakonodajam po svetu so ženske v nekaterih poklicih še vedno žrtve neposredne diskriminacije. Kot je zapisano na omenjeni spletni strani, navadno ločimo posredno in neposredno diskriminacijo. Slednja nastopi, kadar je človek zaradi določene osebne okoliščine brez upravičenega razloga obravnavan manj ugodno kot nekdo drug v enakem ali podobnem položaju. Gre predvsem za diskriminatorna dejanja na področju razpisov za delovna mesta ter prekinitve delovnih razmerij zaradi spola, invalidnosti ali starosti. O posredni diskriminaciji pa lahko govorimo, kadar delodajalci od kandidatov za delovna mesta zahtevajo izpolnjevanje določenih pogojev, ki za opravljanje dela niso potrebni, in tako določeno skupino postavljajo v slabši položaj v primerjavi z drugimi, še pojasnjujejo na omenjeni strani.",
  "model_name": "sloberta-squad2-SLO"
}'
```

Example output with top 3 answers:
```
[
  {
    "score": 0.07496260106563568,
    "start": 80,
    "end": 108,
    "answer": " www.protidiskriminaciji.si,"
  },
  {
    "score": 0.04607750475406647,
    "start": 80,
    "end": 108,
    "answer": " www.protidiskriminaciji.si,"
  },
  {
    "score": 0.03630998358130455,
    "start": 66,
    "end": 108,
    "answer": " spletna stran www.protidiskriminaciji.si,"
  }
]
```

#### Live demo

The WebAPI can be tested live at http://164.8.252.73:8008/docs



---

> Operacijo Razvoj slovenščine v digitalnem okolju sofinancirata Republika Slovenija in Evropska unija iz Evropskega sklada za regionalni razvoj. Operacija se izvaja v okviru Operativnega programa za izvajanje evropske kohezijske politike v obdobju 2014-2020.

![](Logo_EKP_sklad_za_regionalni_razvoj_SLO_slogan.jpg)
