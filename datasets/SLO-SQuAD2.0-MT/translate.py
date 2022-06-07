import pandas as pd
import re
import csv
from tqdm import tqdm
from datasets import load_dataset, Dataset, DatasetDict
from translatepy.translators.google import GoogleTranslate # use GoogleTranslate

###################
# utility functions

# utility >> get_translation << gets translation into language of the input with the translator 
def get_translation(input, translator, language):
    result = ''
    try:
        translation = translator.translate(input, language)
    except Exception as e:
        print('Exception caught during translation!')
    #print(e)
    else:
        result = translation.result
    return result

# utility >> handle_translation << returns the translated answer, its index, and the translation 
pattern = re.compile("\[___\](.*?)\[___\]") # fixed pattern to annotate the answer " text ... [___] ANSWER [___] ... text "

def handle_translation(translation):
    try:
        match = pattern.search(translation)

        if (match != None):
            old = match.group(0) # answer with tags
            new = match.group(1) # matched answer without tags
            fixed_translation = translation.replace(old, new, 1) # replace to get context without tags
            index = fixed_translation.index(new) # find the index of the answer
        else:
            return '', -1, translation
    except Exception as e: 
        print('Exception caught during translation handling!')
        print(e)
        return '', -1, translation
    else:
        return new, index, fixed_translation # return the answer, its starting index and the handled translation

# utility >> translate_squad2 << handles the translation process
def translate_squad2(df, split):
    prefix = 'slo-squad2-mt-'
    # translation variables
    google_mt = GoogleTranslate()
    language = 'Slovene'
    TAG = '[___]'
    error_ids = []

    slo_df = df.copy(deep=True) # get a deep copy of data

    print(f'Starting machine translation of SQuAD2.0-{split} to {language} ({prefix}{split})...')
    # for each sample
    for row_idx, row_data in tqdm(slo_df.iterrows(), total = len(slo_df)):
        error = False

        # get row data
        id = row_data['id']
        title = row_data['title']
        context = row_data['context']
        question = row_data['question']
        answers = row_data['answers']

        # translate title
        tran_title = get_translation(title, google_mt, language)

        # translate question
        tran_question = get_translation(question, google_mt, language)

        # translate context
        tran_context = get_translation(context, google_mt, language)
            
        # for each context and answer combo, tag the answer within the context, translate both, then remove the tag and store correct answer index in a dictionary
        answer_idx = list(zip(answers['text'], answers['answer_start'])) # make (answer, index) tuples from text and answer_start

        # if answers available, handle them, else set no answers
        if (len(answers['text']) != 0):
            for ans_idx, ai in enumerate(answer_idx):
                what = ai[0] # text
                idx = ai[1] # answer_start
                
                tagged_context = context.replace(what, TAG + what + TAG, 1)   # tag the context

                # translate the tagged context
                tran_tagged_context = get_translation(tagged_context, google_mt, language)

                # extract the translated answer and store the correct index within the context
                tran_answer, answer_index, tran_context_handled = handle_translation(tran_tagged_context)

                if(tran_answer != '' and answer_index != -1):
                    # store new answers and their indices
                    # list-tuple workaround to change values
                    lst = list(answer_idx[ans_idx])
                    lst[0] = tran_answer
                    lst[1] = answer_index
                    tpl = tuple(lst)
                    answer_idx[ans_idx] = tpl      
                else:  # error, stop and skip this sample
                    error = True
                    break

            # if there was an error, save the id where it occurred and continue
            if(error == True):
                error_ids.append((row_idx, id)) # append tuple (row_index, id)
                error = False
                continue

            # invert zip operation
            inv = list(zip(*answer_idx))
            try:
                tran_answers = {'text': list(inv[0]), 'answer_start': list(inv[1])}
            except Exception as e:
                tran_answers = {'text': [], 'answer_start': []} # if error, set to no answers
                #print(e)

        else:
            #print(f'No answers detected at question id= {id} ! Skipping answer tagging...')
            tran_answers = {'text': [], 'answer_start': []} # if no answers available, set to no answers

        # update row with translations
        slo_df.loc[row_idx, ['title', 'context', 'question', 'answers']] = [tran_title, tran_context, tran_question, tran_answers]

    print('#########################################')
    print(f'Errors: {len(error_ids)} ({(len(error_ids)/len(slo_df) * 100):.2f}%)')
    errors_path = f'errors-{split}.csv'
    print(f'Saving errors to {errors_path}...')
    with open(errors_path, 'w') as f:
        csv_file = csv.writer(f)
        csv_file.writerow(['row_idx', 'id'])
        for row in error_ids:
            csv_file.writerow(row)

    print(f'\nSaving dataset into Huggingface Dataset format...')
    slo_squad2 = Dataset.from_pandas(slo_df)# make a Dataset class from Pandas

    print(f'Saving dataset to JSON')
    slo_squad2.to_json(f'{prefix}{split}.json')

    print(f'Saving dataset to disk (extended format)')
    slo_squad2.save_to_disk(f'{prefix}{split}')

    print(f'{prefix}{split} size: {len(slo_squad2)-len(error_ids)} ({((len(slo_squad2)-len(error_ids))/len(df) * 100):.2f}% of SQuAD2.0)')


# main function call
def main():
    # load original dataset
    squad_v2 = load_dataset('squad_v2')

    # get validation split
    #squad_val = squad_v2['validation'] # change/add 'train' for training

    # get train split
    squad_train = squad_v2['train'] 

    # convert validation split to Pandas DataFrame
    df = pd.DataFrame(squad_train)

    # call translation handler
    translate_squad2(df, 'train') # change/add 'train' for training


if (__name__ == "__main__"):
    main()