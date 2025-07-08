import json
from tqdm import tqdm
import argparse
from util.random_util import weighted_sample
import yaml
import os
from util.scale_util import scales_dict
os.system('clear')


parser = argparse.ArgumentParser()
parser.add_argument("--batch_index", default=0, help="batch_index", type=int)
parser.add_argument("--n_epoch", default=400, help="n_epoch", type=int)
parser.add_argument("--data_dir", default='./data/music', help="data_dir", type=str)
args = parser.parse_args()


def ordinal(n):
    """Converts an integer to its ordinal string representation (1 → 1st, 2 → 2nd, etc.)."""
    if 11 <= n % 100 <= 13:  # Handle 11th, 12th, 13th
        return f"{n}th"
    elif 1 <= n % 10 <= 3:
        return f"{n}{['th', 'st', 'nd', 'rd'][n % 10]}"
    else:
        return f"{n}th"


def convert_bar_whqes(bar):

    whqes_map = {'1/2': 'h', '1/4': 'q', '1/8': 'e', '1/16': 's', '3/16': 'e.', 
                 '7/16': 'q..', '3/8': 'q.', '3/4': 'h.', '7/8': 'h..'}
    
    out_dict = dict()

    if 'treble' in bar.keys():
        note_list = bar['treble']
        pitch_list = [x['pitch'] for x in note_list]
        duration_list = [whqes_map[x['duration']] for x in note_list]
        tie_list = ['~' if 'tie' in x.keys() else '' for x in note_list]

        out_dict['treble_pitch'] = pitch_list
        out_dict['treble_tempo'] = [f'{d}{tie}' for (d, tie) in zip(duration_list, tie_list)]
        out_dict['treble_all'] = [f'{t}{p}{tie}' for (t, p, tie) in zip(duration_list, pitch_list, tie_list)]
    
    if 'bass' in bar.keys():
        note_list = bar['bass']
        pitch_list = [x['pitch'] for x in note_list]
        duration_list = [whqes_map[x['duration']] for x in note_list]
        tie_list = ['~' if 'tie' in x.keys() else '' for x in note_list]

        out_dict['bass_pitch'] = pitch_list
        out_dict['bass_tempo'] = [f'{d}{tie}' for (d, tie) in zip(duration_list, tie_list)]
        out_dict['bass_all'] = [f'{t}{p}{tie}' for (t, p, tie) in zip(duration_list, pitch_list, tie_list)]

    for k in out_dict.keys():
        out_dict[k] = ' '.join(out_dict[k])

    if 'bass' in bar.keys() and 'treble' in bar.keys():
        
        out_dict['both_pitch'] = 'treble: ' + out_dict['treble_pitch'] + '\n' + 'bass: ' + out_dict['bass_pitch']
        out_dict['both_tempo'] = 'treble: ' + out_dict['treble_tempo'] + '\n' + 'bass: ' + out_dict['bass_tempo']
        out_dict['both_all'] = 'treble: ' + out_dict['treble_all'] + '\n' + 'bass: ' + out_dict['bass_all']

    return out_dict


def generate_questions(meta, config):

    time_signature = meta['time_signature']
    title_str = config['title_str']
    author_str = config['author_str']
    tempo = meta['tempo']
    key = meta['key']

    key_root = key.split(' ')[0]
    scale_tyle = key.split(' ')[1]

    key_notes = scales_dict[scale_tyle][key_root]
    # print('key', key, 'key_notes', key_notes)

    n_bar = config['n_bar']
    notes = json.dumps(meta['bars'], indent=0)
    repeat_interval = config['repeat_interval']

    if config['treble'] and config['bass']:
        clef_answer = 'The music sheet includes both treble and bass clefs.'
    elif config['treble'] and not config['bass']:
        clef_answer = 'The music sheet only has a treble clef.'
    elif not config['treble'] and config['bass']:
        clef_answer = 'The music sheet only has a bass clef.'
    else:
        raise Exception('Must has at least one clef.')
    
    if repeat_interval is None:
        repeat_answer = 'It does not contain any repeating bars.'
    else:
        repeat_answer = f'It shows repeat bars from the {ordinal(repeat_interval[0])} bar and {ordinal(repeat_interval[1])} bar.'

    
    static_question_templates = {
            'Title': ["What is the title of the music sheet?", title_str],
            'Author': ["Who is the composer of this piece?", author_str],
            'key': ["What scale is this music in?", f'{key} scale'],
            'key_notes': [f"What are all the notes in the {key} scale?", ' '.join(key_notes)],
            'BPM': ["What is the tempo in BPM?", f'{tempo} BPM'],
            'Clef': ['What clef is included in the music sheet?', clef_answer],
            'n_bar': ["How many measures are in the music sheet?", f'{n_bar} measures / bars'],
            'time_signature': ["What is the time signature?", time_signature],
            'repeat': ["Does this music sheet contain repeat sections?", repeat_answer],
    }

    dynamic_question_templates = {
            'omr_bar_treble': "Please extract the pitch and duration of all notes in the x-th bar of the treble clef.",
            'omr_bar_bass': "Please extract the pitch and duration of all notes in the x-th bar of the bass clef.",
            'omr_bar_both': "Please extract the pitch and duration of all notes in the x-th bar for both treble and bass clefs.",
            'omr_bar_treble_pitch': "Please extract the pitch of all notes in the x-th bar of the treble clef.",
            'omr_bar_bass_pitch': "Please extract the pitch of all notes in the x-th bar of the bass clef.",
            'omr_bar_both_pitch': "Please extract the pitch of all notes in the x-th bar of the treble and bass clefs.",
            'omr_bar_treble_tempo': "Please extract the tempo of all notes in the x-th bar of the treble clef.",
            'omr_bar_bass_tempo': "Please extract the tempo of all notes in the x-th bar of the bass clef.",
            'omr_bar_both_tempo': "Please extract the tempo of all notes in the x-th bar of the treble and bass clefs.",
            'chord_bar_show': "What is the chord of the x-th bar?",
            'chord_bar_estimate': "What might be a good chord for the x-th bar?",
            'chord_full_show': "Please extract all the chords from each bar.",
    }

    # Generate Q&A dynamically
    questions = []

    for x_bar_index in weighted_sample(range(n_bar),  k=min(1, n_bar), weights='uniform'):
        bar_info = convert_bar_whqes(meta['bars'][x_bar_index]['staves'])


        for q_type in dynamic_question_templates.keys():

            question = dynamic_question_templates[q_type]
            question = question.replace('x-th', f'{ordinal(x_bar_index + 1)}')

            if q_type == 'omr_bar_both' and config['treble'] and config['bass']:
                answer = bar_info['both_all']
            elif q_type == 'omr_bar_both_pitch' and config['treble'] and config['bass']:
                answer = bar_info['both_pitch']
            elif q_type == 'omr_bar_both_tempo' and config['treble'] and config['bass']:
                answer = bar_info['both_tempo']

            elif q_type == 'omr_bar_treble' and config['treble']:
                answer = bar_info['treble_all']
            elif q_type == 'omr_bar_treble_pitch' and config['treble']:
                answer = bar_info['treble_pitch']
            elif q_type == 'omr_bar_treble_tempo' and config['treble']:
                answer = bar_info['treble_tempo']

            elif q_type == 'omr_bar_bass' and config['bass']:
                answer = bar_info['bass_all']
            elif q_type == 'omr_bar_bass_pitch' and config['bass']:
                answer = bar_info['bass_pitch']
            elif q_type == 'omr_bar_bass_tempo' and config['bass']:
                answer = bar_info['bass_tempo']
            

            elif q_type == 'chord_bar_show' and config['show_chord']:    
                answer = meta['bars'][x_bar_index]['chord'] + ' chord'
            elif q_type == 'chord_full_show' and config['show_chord']:
                answer = ' - '.join([x['chord'] for x in meta['bars']])
            elif q_type == 'chord_bar_estimate' and not config['show_chord']:
                answer = meta['bars'][x_bar_index]['chord'] + ' chord'
            else:
                continue

            questions.append([question, answer])
    
    return questions


if __name__=='__main__':

    
    all_data = sorted([x for x in os.listdir(args.data_dir) if x != '.DS_Store'])
    l = len(all_data)

    split_th = int(l * 0.9)

    train_data = all_data[:split_th]
    test_data = all_data[split_th:]


    qa_meta = []
    for doc_id in tqdm(test_data):

        meta = json.load(open(os.path.join(args.data_dir, doc_id, f'{doc_id}.json')))

        config = yaml.unsafe_load(open(os.path.join(args.data_dir, doc_id, f'{doc_id}_config.yaml'), "r"))  # Use safe_load to avoid security issues

        qa_list = generate_questions(meta, config)

        for question, answer in qa_list:
            qa_meta.append({'doc_id': doc_id, 'question': question, 'answer': answer, 'encode_format': config['encode_format']})

    json.dump(qa_meta, open('./data/test_qa_long.json', 'w'), indent=2)


    qa_meta = []
    for doc_id in tqdm(train_data):

        meta = json.load(open(os.path.join(args.data_dir, doc_id, f'{doc_id}.json')))
        config = yaml.unsafe_load(open(os.path.join(args.data_dir, doc_id, f'{doc_id}_config.yaml'), "r"))  # Use safe_load to avoid security issues
        qa_list = generate_questions(meta, config)

        for question, answer in qa_list:
            qa_meta.append({'doc_id': doc_id, 'question': question, 'answer': answer, 'encode_format': config['encode_format']})

    json.dump(qa_meta, open('./data/train_qa_long.json', 'w'), indent=2)




    