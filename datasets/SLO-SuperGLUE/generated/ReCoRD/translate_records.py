####### Imports #######
import re
import traceback
from os import replace
from os.path import splitext
import os
import time
from random import randint
from json import decoder, dump, load, dumps
from translatepy.translators.google import GoogleTranslateV2


####### Utils #######
class DataIO:
    def save_json(self, filename, data, sort_keys=True):
        """Atomically save a JSON file given a filename and a dictionary."""
        path, _ = splitext(filename)
        tmp_file = "{}.{}.tmp".format(path, randint(1000, 999999))
        with open(tmp_file, 'w', encoding='utf-8') as f:
            dump(data, f, indent=4, sort_keys=sort_keys, separators=(',', ' : '), ensure_ascii=False)
        try:
            with open(tmp_file, 'r', encoding='utf-8') as f:
                data = load(f)
        except decoder.JSONDecodeError:
            print("Attempted to write file {} but JSON "
                  "integrity check on tmp file has failed. "
                  "The original file is unaltered."
                  "".format(filename))
            return False
        except Exception as e:
            print('A issue has occured saving ' + filename + '.\n'
                                                             'Traceback:\n'
                                                             '{0} {1}'.format(str(e), e.args))
            return False

        replace(tmp_file, filename)
        return True

    def load_json(self, filename):
        """Load a JSON file and return a dictionary."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = load(f)
            return data
        except Exception as e:
            print('A issue has occured loading ' + filename + '.\n'
                                                              'Traceback:\n'
                                                              '{0} {1}'.format(str(e), e.args))
            return {}

    def append_json(self, filename, data):
        """Append a value to a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                file = load(f)
        except Exception as e:
            print('A issue has occured loading ' + filename + '.\n'
                                                              'Traceback:\n'
                                                              '{0} {1}'.format(str(e), e.args))
            return False
        try:
            file.append(data)
        except Exception as e:
            print('A issue has occured updating ' + filename + '.\n'
                                                               'Traceback:\n'
                                                               '{0} {1}'.format(str(e), e.args))
            return False
        path, _ = splitext(filename)
        tmp_file = "{}.{}.tmp".format(path, randint(1000, 999999))
        with open(tmp_file, 'w', encoding='utf-8') as f:
            dump(file, f, indent=4, sort_keys=True, separators=(',', ' : '))
        try:
            with open(tmp_file, 'r', encoding='utf-8') as f:
                data = load(f)
        except decoder.JSONDecodeError:
            print("Attempted to write file {} but JSON "
                  "integrity check on tmp file has failed. "
                  "The original file is unaltered."
                  "".format(filename))
            return False
        except Exception as e:
            print('A issue has occured saving ' + filename + '.\n'
                                                             'Traceback:\n'
                                                             '{0} {1}'.format(str(e), e.args))
            return False

        replace(tmp_file, filename)
        return True

    def is_valid_json(self, filename):
        """Verify that a JSON file exists and is readable. Take in a filename and return a boolean."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                load(f)
            return True
        except (FileNotFoundError, decoder.JSONDecodeError):
            return False
        except Exception as e:
            print('A issue has occured validating ' + filename + '.\n'
                                                                 'Traceback:\n'
                                                                 '{0} {1}'.format(str(e), e.args))
            return False

    def create_file_if_doesnt_exist(self, filename, whatToWriteIntoIt):
        if not os.path.exists(filename):
            with open(filename, 'w') as f: f.write(whatToWriteIntoIt)


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:
    def __init__(self, info_text, start=False, use_logger=None):
        self._start_time = None
        self.info_text = info_text
        self.previous_time = 0
        self.use_logger = use_logger
        if start:
            self.start()

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self.previous_time = elapsed_time
        self._start_time = None
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
              f"INFO (time): {self.info_text} [{elapsed_time:0.4f}s]")
        if self.use_logger is not None:
            self.use_logger.info(f"(time) {self.info_text} -> [{elapsed_time:0.4f}s]")
        # print(f"Elapsed time: {elapsed_time:0.4f} seconds")

    def stop_and_return_elapsed(self):
        """Stop the timer, and return time elapsed"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self.previous_time = elapsed_time
        self._start_time = None
        return elapsed_time

    def current_or_total_time(self):
        """Get the current time if the timer is running, or the previous_time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        return time.perf_counter() - self._start_time

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()

    def __del__(self):
        self._start_time = None


####### Global variables #######
ReCoRD_file_names = ['dev.json', 'train.json']
ReCoRD_json_folder_in = 'ReCoRD_Original'  # original (forigen language)
ReCoRD_json_folder_out = 'ReCoRD_Slo_Translated'  # output (target language)
translation_args = {"destination_language": "sl", "source_language": "en"}
# N will be replaced with entity index
placeholder_TAG = '[_N_]'
placeholder_TAG_variations = ['[_N_ ]', '[ _N_]', '[ _N_ ]']
get_nums_pattern = re.compile(r'\[_(\d+)_]')
pattern_for_splitting = re.compile(r'\[_\d+_]')
translator = GoogleTranslateV2()


####### Methods #######
def get_filled_text_with_tags(original_text, offsets, TAG):
    new_txt = original_text[:offsets[0]['start']]
    for i in range(len(offsets)):
        offset = offsets[i]
        _TAG = TAG.replace('N', str(i))
        new_txt += _TAG + original_text[offsets[i]['start']:offsets[i]['end'] + 1] + _TAG
        if i < len(offsets) - 1:
            new_txt += original_text[offsets[i]['end'] + 1:offsets[i + 1]['start']]
        else:
            new_txt += original_text[offsets[i]['end'] + 1:]
    return new_txt


special_nl = '\n_\n_\n\n_\n_\n'
fod_debugging_purposes_tl = []


def get_translated_text(text_in):
    global fod_debugging_purposes_tl
    translation_args['text'] = text_in
    try:
        text_out = translator.translate(**translation_args)
        text_out = text_in.replace('@poudari', '@highlight')
    except Exception as e:
        print(f'Error at translation: {str(e)}')
        return str(e), False
    ret = str(text_out)
    # for var in placeholder_TAG_variations:
    #    ret = ret.replace(var, placeholder_TAG)
    ret = ret.replace('[ _', '[_')
    ret = ret.replace('_ ]', '_]')  # todo: generalize the variations (aka. placeholder_TAG_variations)
    text_out.result = ret
    # fod_debugging_purposes_tl.append(text_out)  # warning, comment this out when actually running the program
    return ret.split(special_nl), True


def get_new_data(translation, offsets_old, qas_old):
    offsets_new = []
    qas_new = []
    offset_info = {}
    text_tagged = translation[0]
    qas_arr = translation[1:]

    #### double checking section ####
    nums = re.findall(get_nums_pattern, text_tagged)
    if len(nums) % 2 != 0:
        raise Exception("Number of returned entities is not even")
    if len(nums) / 2 != len(offsets_old):
        raise Exception("Number of translated entities does not match the number of the original ones")
    should_be = 0
    entities_correct_order = True
    for i in range(0, len(nums), 2):
        if nums[i] != str(should_be) or nums[i + 1] != str(should_be):
            # raise Exception("Entities in translation are not in correct order")
            entities_correct_order = False
        should_be += 1
    nums = [int(n) for n in nums[::2]]
    #### double checking section ####

    # split_txt = text_tagged.split(placeholder_TAG)
    split_txt = pattern_for_splitting.split(text_tagged)
    j = 0
    off = 0
    probably_ok_splitting = False
    for i in range(0, len(split_txt), 2):
        break_now = False
        if j == len(offsets_old):
            probably_ok_splitting = i == len(split_txt) - 1
            break

        # in case the translation had entities in mixed order, we need to use the old offset value because of the QA part
        idx = nums[j]
        k = f'{offsets_old[idx]["start"]}_{offsets_old[idx]["end"]}'
        s = len(split_txt[i]) + off
        if i != len(split_txt) - 1:
            e = len(split_txt[i + 1]) + s - 1
        else:
            e = off + s
            break_now = True
        offset_info[k] = {'start': s, 'end': e, 'text': split_txt[i + 1]}
        offsets_new.append({'start': s, 'end': e})
        off = e + 1
        j += 1
        if break_now:
            break

    if len(offsets_old) != len(offsets_new) or not probably_ok_splitting:
        raise Exception("Offsets old and new length is not the same. Some translation mishab happened probably.")

    for i, qas in enumerate(qas_old):
        qas_sl = {'id': qas['id'], 'query': qas_arr[i],
                  'answers': [offset_info[f'{ans["start"]}_{ans["end"]}'] for ans in qas['answers']]}
        qas_new.append(qas_sl)

    # text_new = text_tagged.replace(placeholder_TAG, '')
    text_new = pattern_for_splitting.sub('', text_tagged)

    # warning, comment this next line out when actually running the program
    # test_text = get_filled_text_with_tags(text_new, offsets_new, placeholder_TAG)

    return text_new, offsets_new, qas_new


def translate_ReCoRD(rec):
    record_tled = {'version': '1.0', 'data': []}
    record_failed = {'version': '1.0', 'data': []}
    for cnt, r in enumerate(rec['data'], start=1):
        old_offsets = r['passage']['entities']
        old_qas = r['qas']
        with Timer(f"Tagged and translated text of record with id {r['id']} ({cnt}/{len(rec['data'])})") as tim:
            try:
                tagged_text = get_filled_text_with_tags(r['passage']['text'], old_offsets, placeholder_TAG)
                qas = special_nl.join([q['query'] for q in r['qas']])
                tl, succ = get_translated_text(f'{tagged_text}{special_nl}{qas}')
                if tl and succ:
                    new_text, new_offsets, new_qas = get_new_data(tl, old_offsets, old_qas)
                    r['passage']['text'] = new_text
                    r['passage']['entities'] = new_offsets
                    r['qas'] = new_qas
                    record_tled['data'].append(r)
                else:
                    raise Exception(f"Couldn't translate {r['id']} ({str(tl)})")
            except Exception as e:
                err = dumps(f'Error at translation: {str(e)}\ntraceback:{traceback.format_exc()}')
                print(err)
                r['error_becasue'] = err
                record_failed['data'].append(r)
                tim.info_text = tim.info_text.replace('Tagged and translated', '(FAIL) Tagged and translated')
    return record_tled, record_failed


####### Main #######
if __name__ == '__main__':
    if not os.path.exists(ReCoRD_json_folder_out): os.mkdir(ReCoRD_json_folder_out)

    for fn in ReCoRD_file_names:
        file = f'{ReCoRD_json_folder_in}/{fn}'
        if not os.path.exists(file):
            print(f'{file} does not exist!')
            continue
        print(f'Translating {file}')
        try:
            ReCoRD_Original = DataIO().load_json(file)
            ReCoRD_Translated, failed = translate_ReCoRD(ReCoRD_Original)
            print(f'Saving new ReCoRD json for {fn}')
            DataIO().save_json(f'{ReCoRD_json_folder_out}/{fn}', ReCoRD_Translated, sort_keys=False)
            if len(failed['data']) > 0:
                DataIO().save_json(f'{ReCoRD_json_folder_out}/failed-{fn}', failed, sort_keys=False)
        except:
            print(f'Error at file {file}\nTraceback:\n{traceback.format_exc()}')
    print("Done")
