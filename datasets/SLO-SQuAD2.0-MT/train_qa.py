from datasets import load_dataset
from txtai.pipeline import HFTrainer

def main():
    # load dataset
    print('Loading SLO-SQuAD2-MT dataset...')
    slo_squad_mt_v2 = load_dataset('json', data_files={'train': 'data/slo-squad2-mt-train.json', 'validation': 'data/slo-squad2-mt-val.json'})

    trainer = HFTrainer()
    base_model = 'EMBEDDIA/sloberta' # SloBERTa base
	#'google/bert_uncased_L-2_H-128_A-2' # BERT tiny
	#'google/bert_uncased_L-12_H-768_A-12' # BERT base
	#'xlm-roberta-base' # XLM-RoBERTa base
	#'roberta-base' # RoBERTa base
	#'EMBEDDIA/sloberta' # SloBERTa base
    train_data = slo_squad_mt_v2['train'] #.select(range(3000)) 
    val_data = slo_squad_mt_v2['validation'] #.select(range(500))

    n_epochs = 5

    print(f'Running trainer...{base_model}')


    model, tokenizer = trainer(base_model, train_data, task='question-answering', output_dir='results/sloberta-slo-squad_v2', num_train_epochs=n_epochs, do_eval=True, evaluation_strategy='epoch', validation=val_data)
    print('Training complete')
    

if (__name__ == "__main__"):
    main()
