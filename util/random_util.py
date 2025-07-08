import random
import shutil
import math
import numpy as np
from util.note_mapping import *
from util.scale_util import scales_dict
from util.scale_util import get_chord_notes
import string

def generate_random_word(length=5):
    """Generate a random word with the given length."""
    return ''.join(random.choices(string.ascii_lowercase, k=length)).capitalize()

def generate_name():
    """Generate a random name with 1 to 3 words, first letter capitalized."""
    num_words = random.randint(1, 3)
    return ' '.join(generate_random_word(random.randint(3, 8)) for _ in range(num_words))

def generate_title():
    """Generate a random title with 1 to 10 words, first letter capitalized."""
    num_words = random.randint(1, 10)
    return ' '.join(generate_random_word(random.randint(3, 8)) for _ in range(num_words))


def weighted_sample(input_list, k, weights='uniform', std_dev=1):
    """
    Perform weighted sampling from an input list.
    
    Args:
        input_list (list): The list of items to sample from.
        k (int): Number of items to sample.
        weights (str): uniform or gaussian
        std_dev (float): Standard deviation of the Gaussian distribution.
                         Controls the spread of the weights. Default is 1.5.
                         
    Returns:
        list: A list of sampled items.
    """

    assert isinstance(weights, list) or weights in {"uniform", "gaussian"}

    if weights == 'gaussian':
        # Length of the input list
        size = len(input_list)
        
        # Calculate the mean (center of the Gaussian distribution)
        mean = size // 2  # Center index of the list
        
        # Generate Gaussian weights
        weights = [math.exp(-((i - mean) ** 2) / (2 * std_dev ** 2)) for i in range(size)]
        
        # Normalize the weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Perform weighted sampling with replacement
        sampled_items = random.choices(input_list, weights=normalized_weights, k=k)

    elif weights == 'uniform':
        sampled_items = random.choices(input_list, k=k)

    elif isinstance(weights, list):
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        sampled_items = random.choices(input_list, weights=normalized_weights, k=k)
    
    return sampled_items



def generate_random_tempo(beat_per_bar=4, beat_length=4, n_notes=8):
    """
    Generate a random rhythmic pattern for one bar of music by dividing 16 positions.
    Args:
        beat_per_bar (int): Number of beats in the bar.
        beat_length: note of a beat. 4 is for 4th note, 8 is for 8th note
    Returns:
        list: A list of note durations (in 16th notes).
    """
    positions = beat_per_bar * int(16 / beat_length)  # Total 16th note positions
    divisions = sorted(random.sample(range(1, positions), n_notes-1))  # Insert division points
    divisions = [0] + divisions + [positions]  # Add start and end points

    # Calculate the lengths of the notes
    note_list = [divisions[i + 1] - divisions[i] for i in range(len(divisions) - 1)]
    
    return note_list

def generate_random_pitches(scale_type='Major', scale_root='C', n_notes=8, chord_index=1, clef='treble', weights='gaussian', std_dev=1):

    scale_notes = scales_dict[scale_type][scale_root]

    # get all notes in the chord
    chord_notes = get_chord_notes(scale_notes, chord_index)
    chord_notes = [x[0] for x in chord_notes]

    # get all notes for clef and get all notes code for MusiXTEX
    if clef == 'treble':
        chords_notes_all = [x for x in treble_note2code.keys() if x[0] in chord_notes]
        chords_notes_all_code = [treble_note2code[x] for x in chords_notes_all]
    elif clef == 'bass':
        chords_notes_all = [x for x in bass_note2code.keys() if x[0] in chord_notes]
        chords_notes_all_code = [bass_note2code[x] for x in chords_notes_all]
    else:
        raise Exception('clef must be treble or bass')

    # sample pitch for tempo
    # pitch_list = random.choices(chords_notes_all_code, k=n_notes)
    pitch_list = weighted_sample(chords_notes_all_code,  k=n_notes, weights=weights, std_dev=std_dev)

    return pitch_list



