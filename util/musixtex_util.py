import json
import os
import random
import shutil
import subprocess
import math
import numpy as np
from util.note_mapping import *
from util.scale_util import get_chord_symbol
from util.config_util import MusicConfig
from util.random_util import weighted_sample, generate_random_pitches, generate_random_tempo
from util.music_record import MusicComposition

os.system('clear')
header = open('util/header.txt', 'r')
HEADER = ''.join([line for line in header])


def beat_split(tempo_list, pitch_list, beat_len=4):
    beat_len_list = []
    beat_pitch_list = []
    connect_list = []

    len_temp = []
    pitch_temp = []

    for t, p in zip(tempo_list, pitch_list):
        while t > 0:
            available_space = beat_len - sum(len_temp)

            if t <= available_space:
                # Add the entire value to the current beat
                len_temp.append(t)
                pitch_temp.append(p)
                t = 0

                if sum(len_temp) == beat_len:
                    # Current beat is full
                    beat_len_list.append(len_temp)
                    beat_pitch_list.append(pitch_temp)
                    connect_list.append(0)
                    len_temp = []
                    pitch_temp = []
            else:
                # Fill the current beat and carry over the rest
                len_temp.append(available_space)
                pitch_temp.append(p)
                t -= available_space
                beat_len_list.append(len_temp)
                beat_pitch_list.append(pitch_temp)
                connect_list.append(1)
                len_temp = []
                pitch_temp = []
    
    # merge quarters to half
    i = 0
    while i < len(beat_len_list) - 1:
        # Check if the condition is met
        if beat_len_list[i] == [4] and beat_len_list[i + 1] == [4] and connect_list[i] == 1:
            # Merge the lists and update a[i+1]
            beat_len_list[i + 1] = [8]
            # Remove the current entry a[i] and b[i]
            beat_len_list.pop(i)
            beat_pitch_list.pop(i)
            connect_list.pop(i)

        else:
            # Move to the next index only if no merge occurs
            i += 1
            

    return beat_len_list, beat_pitch_list, connect_list


def auto_beam(beat_pitch, clef='treble'):

    # get code2index dict
    if clef == 'treble':
        code2index = treble_code2index
        index2code = treble_code
    elif clef == 'bass':
        code2index = bass_code2index
        index2code = bass_code
    else:
        raise Exception('clef must be treble or bass')
    
    # compute stem direction
    indices = [code2index[p] for p in beat_pitch]
    if np.mean(indices) <= 9:
        stem_pos = 'u'
    else:
        stem_pos = 'l'

    # compute tilt level
    if abs(indices[0] - indices[-1]) <= 2:
        tilt = '0'
        tilt_v = 0
    else:
        v = 1 + int(abs(indices[0] - indices[-1])/2)
        tilt_v = v + -2 * v * (indices[0] > indices[-1])
        tilt = '{' + str(tilt_v) + '}'
    
    # compute beam pos
    if stem_pos == 'u':
        beam_pos_index = max(indices) - (tilt_v>0) * tilt_v
        beam_pos_index = max(beam_pos_index, indices[0]-3)
        beam_pos_index = min(beam_pos_index, 16)
    else:
        beam_pos_index = min(indices) - (tilt_v<0) * tilt_v
        beam_pos_index = min(beam_pos_index, indices[0]+3)
        beam_pos_index = max(beam_pos_index, 5)

    beam_pos = index2code[beam_pos_index]

    return stem_pos, tilt, beam_pos

def compile_musicpdf(s, save_dir='sythetic-music-sheet', work_dir: str='', show_log=False):
    """
    Compiles a LaTeX-based music sheet into a PDF, supporting both Windows and Linux/macOS.

    Args:
        s (str): LaTeX content for the music sheet.
        save_dir (str, optional): Name of the output folder.
        work_dir (str, optional): Working directory path.
    """
    work_dir = os.path.join(work_dir, save_dir)
    
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    else:
        # Remove everything in the directory
        for item in os.listdir(work_dir):
            item_path = os.path.join(work_dir, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Remove files and symbolic links
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Remove directories
        
    # Write LaTeX file
    with open(os.path.join(work_dir, "music_sheet.tex"), 'w') as f_out:
        f_out.writelines(s)
    
    if show_log:
        os.system(f'latex -output-directory={work_dir} {work_dir}/music_sheet.tex')
        os.system(f'musixflx {work_dir}/music_sheet.tex')
        os.system(f'pdflatex -output-directory={work_dir} {work_dir}/music_sheet.tex')
    else:
        # Determine null device (Windows: 'nul', Linux/macOS: '/dev/null')
        null_device = 'nul' if os.name == 'nt' else '/dev/null'

        # Suppress output by redirecting stdout and stderr
        with open(null_device, 'w') as devnull:
            subprocess.run(f'latex -output-directory={work_dir} {work_dir}/music_sheet.tex', 
                           shell=True, stdout=devnull, stderr=devnull)
            subprocess.run(f'musixflx {work_dir}/music_sheet.tex', 
                           shell=True, stdout=devnull, stderr=devnull)
            subprocess.run(f'pdflatex -output-directory={work_dir} {work_dir}/music_sheet.tex', 
                           shell=True, stdout=devnull, stderr=devnull)

    return 0


def encode_bar_note(tempo_list, pitch_list, clef='treble'):

    if clef == 'treble':
        code2index = treble_code2index
    elif clef == 'bass':
        code2index = bass_code2index
    else:
        raise Exception('clef must be treble or bass')
    
    note_len_dict = {1: '\\cca {@}', 2: '\\ca {@}', 3: '\\cap {@}', 4: '\\qa {@}', 5: '\\islurd0@\\qa @ \\tslur0@\\cca @', 
                 6: '\\qap {@}', 7: '\\qapp {@}', 8: '\\ha {@}', 9: '\\islurd0@\\ha @ \\tslur0@ \\cca @', 
                 10: '\\islurd0@\\ha @ \\tslur0@ \\ca @', 11: '\\islurd0@ \\ha @ \\tslur0@ \\cap @', 
                 12: '\\hap {@}', 13: '\\islurd0@\\hap @ \\tslur0@\\ccap @', 14: '\\happ {@}', 
                 15: '\\islurd0@\\hap @ \\tslur0@\\cap @', 16: '\\wh {@}'}

    bar_str = ''
    for t, p in zip(tempo_list, pitch_list):
        p_index = code2index[p]
        if p_index <= 10:
            stem_pos = 'u'
        else:
            stem_pos = 'l'

        note_code = note_len_dict[t]
        note_code = note_code.replace('a', stem_pos)
        note_code = note_code.replace('@', f'{p}')

        bar_str += note_code + ' '

    return bar_str


def encode_bar_beat(tempo_list, pitch_list, clef='treble'):
    
    bar_str_list = []
    beat_len_list, beat_pitch_list, connect_list = beat_split(tempo_list, pitch_list)
    
    for beat_len, beat_pitch, connect in zip(beat_len_list, beat_pitch_list, connect_list):

        stem_pos, tilt, beam_pos = auto_beam(beat_pitch, clef=clef)

        beat_len_str = ''.join([str(x) for x in beat_len])

        if beat_len_str == '1111':
            beat_str = '\\Qqbb' + stem_pos + ' ' + ''.join(beat_pitch) + '{connect}'
            beat_str = '\\ibb{stem_pos}0{Ps}{tilt}\\qb0{' + '{P0}{P1}{P2}' + '}{connect}\\tq{stem_pos}0{P3}'
        elif beat_len_str == '22':
            beat_str = '\\ib{stem_pos}0{Ps}{tilt}\\qb0{P0}{connect}\\tq{stem_pos}0{P1}'
        elif beat_len_str == '4':
            beat_str = '{connect}' + '\\q' + stem_pos + ' {{P0}}'
        elif beat_len_str == '8':
            beat_str = '{connect}' + '\\h' + stem_pos + ' {{P0}}'
        elif beat_len_str == '13':
            beat_str = '\\ibb{stem_pos}0{Ps}{tilt}\\roff{\\tbb{stem_pos}0}\qb0{P0}\\tb{stem_pos}0{connect}\\qbp0{P1}'
        elif beat_len_str == '31':
            beat_str = '\\ib{stem_pos}0{Ps}{tilt}\\qbp0{{P0}}\\tbb{stem_pos}0{connect}\\tq{stem_pos}0{P1}'
        elif beat_len_str == '112':
            beat_str = '\\ibb{stem_pos}0{Ps}{tilt}\qb0{{P0}}\\tbb{stem_pos}0\\qb0{{P1}}{connect}\\tq{stem_pos}0{P2}'
        elif beat_len_str == '121':
            beat_str = '\\ibb{stem_pos}0{Ps}{tilt}\\roff{\\tbb{stem_pos}0}\\qb0{{P0}{P1}}\\tbb{stem_pos}0{connect}\\tq{stem_pos}0{P2}'
        elif beat_len_str == '211':
            beat_str = '\\ib{stem_pos}0{Ps}{tilt}\\qb0{{P0}}\\nbb{stem_pos}0\\qb0{{P1}}{connect}\\tq{stem_pos}0{P2}'
        else:
            raise NotImplementedError('Not implemented')
        
        beat_str = beat_str.replace('{stem_pos}', stem_pos)
        beat_str = beat_str.replace('{tilt}', tilt)

        beat_str = beat_str.replace('{Ps}', beam_pos)

        for i in range(len(beat_pitch)):
            beat_str = beat_str.replace('{P' + str(i) + '}', beat_pitch[i])

        if connect == 1:
            beat_str = beat_str.replace('{connect}', '\\islurd0{Pc}')
            beat_str += '\\tslur0{Pc}'
            beat_str = beat_str.replace('{Pc}', beat_pitch[-1])
        else:
            beat_str = beat_str.replace('{connect}', '')


        bar_str_list.append(beat_str)

    bar_str = ' '.join(bar_str_list)
    return bar_str


def generate_music(config: MusicConfig):

    scale_name = f'{config.scale_root} {config.scale_type}'

    assert config.spacing in {0, 1, 2, 3, 4}
    spacing_prefix_list = ['\\notes', '\\Notes', '\\NOtes', '\\NOTes', '\\NOTEs']
    spacing_prefix = spacing_prefix_list[config.spacing]

    beat_per_bar, beat_length = config.meterfrac
    scale_index = ScaleName2Index[scale_name]

    header_str = HEADER
    header_str_0 = header_str.replace('Title_str', config.title_str)
    header_str_1 = header_str_0.replace('Author_str', config.author_str)

    
    if config.bass and config.treble:
        generated_musixtex_str = '\n'.join(['\\metron{\\smallnotesize\lqu}{' + str(config.bpm) + '}\\\\', '\parindent 0mm', 
                                            '\\instrumentnumber{1}', '\\smallmusicsize\\bigaccid' if config.smallmusicsize else '', 
                                            '\setname1{' + config.instrument + '}', '\\setstaffs1{2}', '\\generalsignature{' + str(scale_index) + '}', 
                                            '\\setclef1\\bass', '\\generalmeter{' + f'\\meterfrac{beat_per_bar}{beat_length}' + '}', '\\startpiece\n'])
    elif config.treble and not config.bass:
        generated_musixtex_str = '\n'.join(['\\metron{\\smallnotesize\lqu}{' + str(config.bpm) + '}\\\\',
                                            f'\\parindent {config.parindent}mm', '\\instrumentnumber{1}', '\\smallmusicsize\\bigaccid' if config.smallmusicsize else '', 
                                            '\setname1{' + config.instrument + '}', '\\generalsignature{' + str(scale_index) + '}',
                                            '\\generalmeter{' + f'\\meterfrac{beat_per_bar}{beat_length}' + '}', '\\startpiece\n'])
    elif config.bass and not config.treble:
        generated_musixtex_str = '\n'.join(['\\metron{\\smallnotesize\lqu}{' + str(config.bpm) + '}\\\\',
                                            f'\\parindent {config.parindent}mm', '\\instrumentnumber{1}', '\\smallmusicsize\\bigaccid' if config.smallmusicsize else '', 
                                            '\setname1{' + config.instrument + '}', '\\generalsignature{' + str(scale_index) + '}', '\\setclef1\\bass', 
                                            '\\generalmeter{' + f'\\meterfrac{beat_per_bar}{beat_length}' + '}', '\\startpiece\n'])
    else:
        raise Exception('Must have at least one clef, bass or treble')

    bar_str_list = []
    music_data = MusicComposition(tempo=config.bpm, key=scale_name, time_signature=f'{beat_per_bar}/{beat_length}')
    for i in range(config.n_bar):
        
        treble_tempo_list = treble_pitch_list = bass_tempo_list = bass_pitch_list = None
        bar_str_by_clef = []

        if i == 0 or i == config.n_bar-1:
            chord_index = 1
        else:
            chord_index = random.choice(range(1, 7))

        if config.bass:
            n_notes = weighted_sample(range(1, 3 * beat_per_bar),  k=1, weights='gaussian')[0]
            bass_tempo_list = generate_random_tempo(beat_per_bar=beat_per_bar, beat_length=beat_length, n_notes=n_notes)
            bass_pitch_list = generate_random_pitches(scale_type=config.scale_type, scale_root=config.scale_root, chord_index=chord_index, 
                                                 n_notes=n_notes, clef='bass', weights='gaussian', std_dev=1)
            
            if config.encode_format == 'beat':
                bass_bar_str = encode_bar_beat(bass_tempo_list, bass_pitch_list, clef='bass')
            else:
                bass_bar_str = encode_bar_note(bass_tempo_list, bass_pitch_list, clef='bass')

            bar_str_by_clef.append(bass_bar_str)

        if config.treble:
            n_notes = weighted_sample(range(1, 3 * beat_per_bar),  k=1, weights='gaussian')[0]
            treble_tempo_list = generate_random_tempo(beat_per_bar=beat_per_bar, beat_length=beat_length, n_notes=n_notes)
            treble_pitch_list = generate_random_pitches(scale_type=config.scale_type, scale_root=config.scale_root, chord_index=chord_index, 
                                                 n_notes=n_notes, clef='treble', weights='gaussian', std_dev=1)

            if config.encode_format == 'beat':
                treble_bar_str = encode_bar_beat(treble_tempo_list, treble_pitch_list, clef='treble')
            else:
                treble_bar_str = encode_bar_note(treble_tempo_list, treble_pitch_list, clef='treble')

            bar_str_by_clef.append(treble_bar_str)
        
        bar_str = f'% bar {i+1}' + '\n' + f'{spacing_prefix} ' + ' | {chord}'.join(bar_str_by_clef) + '\\en'
        
        chord_symbol = get_chord_symbol(config.scale_type, config.scale_root, chord_index)
        if config.show_chord:
            bar_str = bar_str.replace('{chord}', '\\zchar{18}{' + chord_symbol + '}')
        else:
            bar_str = bar_str.replace('{chord}', '')

        music_data.record_bar(bar_number=i+1, treble_tempo_list=treble_tempo_list, treble_pitch_list=treble_pitch_list, 
                              bass_tempo_list=bass_tempo_list, bass_pitch_list=bass_pitch_list, 
                              encode_format=config.encode_format, chord=chord_symbol.replace('\\', ''))

        bar_str_list.append(bar_str)

    if config.repeat_interval is not None:
        start, end = config.repeat_interval
        music_data.bars[start-1].repeat_start = True
        music_data.bars[end-1].repeat_end = True
        generated_musixtex_str += ('\n\\bar\n'.join(bar_str_list[:start-1]) + '\\leftrepeat' + '\n\\bar\n'.join(bar_str_list[start-1:end]) + '\\rightrepeat' + '\n\\bar\n'.join(bar_str_list[end:]))
    else:
        generated_musixtex_str += '\n\\bar\n'.join(bar_str_list)

    
    if config.barnumber_format == 'system':
        MusixTex_str = header_str_1 + '\n\\begin{music}\n' + '\\systemnumbers\n' + generated_musixtex_str + ' \\mulooseness=1 \\Endpiece\n\\end{music}\n\\end{document}'
    else:
        MusixTex_str = header_str_1 + '\n\\begin{music}\n' + '\\barnumbers\n' + generated_musixtex_str + ' \\mulooseness=1 \\Endpiece\n\\end{music}\n\\end{document}'
    
    return MusixTex_str, music_data

