from util.scale_util import *
from util.note_mapping import *
import random
import os

def synth_progression(scale_type="Major", length=4):
    # Simplified chord indices
    chord_indices = {
        "Diatonic": [0, 1, 2, 3, 4, 5, 6],  # For Major, Dorian, Phrygian, etc.
        "Pentatonic": [0, 1, 2, 3, 4]       # For Pentatonic Major and Pentatonic Minor
    }

    # Map each scale type to its appropriate chord index set
    if 'Pentatonic' in scale_type:
        chords = chord_indices["Pentatonic"]
    else:
        chords = chord_indices["Diatonic"]

    # Define harmonic relationships for each scale
    harmonic_relationships = {
        "Major": {
            0: [4, 3, 5, 1],  # I -> V, IV, vi, ii
            1: [4, 0],        # ii -> V, I
            2: [5, 3],        # iii -> vi, IV
            3: [0, 4, 1],     # IV -> I, V, ii
            4: [0, 5],        # V -> I, vi
            5: [1, 3],        # vi -> ii, IV
            6: [0, 2]         # vii° -> I, iii
        },
        "Dorian": {
            0: [4, 5, 3],     # i -> v, VI, iv
            1: [3, 0],        # ii -> iv, i
            2: [5, 4],        # III -> VI, v
            3: [0, 1, 4],     # iv -> i, ii, v
            4: [0, 6],        # v -> i, VII
            5: [3, 2],        # VI -> iv, III
            6: [0, 4]         # VII -> i, v
        },
        "Phrygian": {
            0: [3, 1],        # i -> iv, II
            1: [5, 4],        # II -> VI, v
            2: [5, 0],        # III -> VI, i
            3: [0, 4],        # iv -> i, v
            4: [0, 6],        # v -> i, VII
            5: [2, 3],        # VI -> III, iv
            6: [1, 0]         # vii -> II, i
        },
        "Lydian": {
            0: [2, 4, 3],     # I -> iii, V, IV
            1: [4, 0],        # II -> V, I
            2: [5, 3],        # iii -> vi, IV
            3: [0, 4],        # IV -> I, V
            4: [0, 2],        # V -> I, iii
            5: [1, 3],        # vi -> II, IV
            6: [0, 2]         # vii° -> I, iii
        },
        "Mixolydian": {
            0: [4, 3, 6],     # I -> V, IV, VII
            1: [4, 0],        # ii -> V, I
            2: [5, 3],        # iii° -> vi, IV
            3: [0, 6],        # IV -> I, VII
            4: [0, 3],        # V -> I, IV
            5: [1, 6],        # vi -> ii, VII
            6: [0, 4]         # VII -> I, V
        },
        "Aeolian": {
            0: [5, 3, 4],     # i -> VI, iv, v
            1: [4, 0],        # ii° -> v, i
            2: [5, 3],        # III -> VI, iv
            3: [0, 4],        # iv -> i, v
            4: [0, 6],        # v -> i, VII
            5: [2, 3],        # VI -> III, iv
            6: [0, 4]         # VII -> i, v
        },
        "Minor": {             # Same as Aeolian
            0: [5, 3, 4],     # i -> VI, iv, v
            1: [4, 0],        # ii° -> v, i
            2: [5, 3],        # III -> VI, iv
            3: [0, 4],        # iv -> i, v
            4: [0, 6],        # v -> i, VII
            5: [2, 3],        # VI -> III, iv
            6: [0, 4]         # VII -> i, v
        },
        "Locrian": {
            0: [1, 3],        # i° -> II, iv
            1: [4, 0],        # II -> v, i°
            2: [5, 3],        # iii -> VI, iv
            3: [0, 4],        # iv -> i°, v
            4: [0, 6],        # V -> i°, VII
            5: [2, 3],        # VI -> iii, iv
            6: [1, 0]         # vii -> II, i°
        },
        "Pentatonic Major": {
            0: [2, 3],        # I -> IV, V
            1: [3, 4],        # ii -> V, vi
            2: [0, 3],        # IV -> I, V
            3: [0, 2],        # V -> I, IV
            4: [0, 2]         # vi -> I, IV
        },
        "Pentatonic Minor": {
            0: [2, 3],        # i -> iv, V
            1: [3, 2],        # III -> V, iv
            2: [0, 1],        # iv -> i, III
            3: [0, 1],        # V -> i, III
            4: [2, 0]         # VII -> iv, i
        }
    }

    # Choose the appropriate harmonic relationships
    relationships = harmonic_relationships[scale_type]

    # Start with the tonic chord (index 0)
    progression = [chords[0]]

    # Generate the progression
    for _ in range(1, length):
        current_chord = progression[-1]
        possible_next_chords = relationships.get(current_chord, chords)
        next_chord = random.choice(possible_next_chords)
        progression.append(next_chord)

    return progression


if __name__=="__main__":
    os.system('clear')

    
    # scale_root = random.choice(note_name)
    # scale_name = random.choice(scale_list)

    scale_root = 'A'
    scale_name = 'Pentatonic Major'

    scale_notes = scales[scale_name][scale_root]


    print(f'{scale_root} {scale_name}', scale_notes)

    for i in range(1, len(scale_notes)+1):

        chords = get_chord_notes(scale_notes, i)
        print(f'{i}-th, chords', chords)

    # chords = generate_scale_info(scale_root, scale_name, chord_name=True)
    # print(chords)
    # # chord_progression = [chords[x] for x in random.choice(chord_progressions_by_scale[scale_name])]
    # # print('chord_progression:\n', chord_progression)
    
    # synthetic_progression = [chords[x] for x in synth_progression(scale_type=scale_name, length=6)]
    # # print('synthetic_progression:\n', synthetic_progression)

    # for chord in synthetic_progression:
    #     root_note, chord_type = chord.split(' ')
    #     chord_notes = get_chord_notes(root_note, chord_type)
    #     print(chord, chord_notes)
