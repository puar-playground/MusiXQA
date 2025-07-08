import os
os.system('clear')
import json

note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'Db', 'Eb', 'Gb', 'Ab', 'Bb']

ScaleName2Index = {'C Major': 0, 'C Minor': -3, 'C# Major': 7, 'C# Minor': 4, 'Cb Major': -7, 'Cb Minor': -10, 
                   'D Major': 2, 'D Minor': -1, 'D# Major': 9, 'D# Minor': 6, 'Db Major': -5, 'Db Minor': -8, 
                   'E Major': 4, 'E Minor': 1, 'Eb Major': -3, 'Eb Minor': -6, 'F Major': -1, 'F Minor': -4, 
                   'F# Major': 6, 'F# Minor': 3, 'Gb Major': -6, 'Gb Minor': -9, 'G Major': 1, 'G Minor': -2, 
                   'G# Major': 8, 'G# Minor': 5, 'Ab Major': -4, 'Ab Minor': -7, 'A Major': 3, 'A Minor': 0, 
                   'A# Major': 10, 'A# Minor': 7, 'Bb Major': -2, 'Bb Minor': -5, 'B Major': 5, 'B Minor': 2}

treble_code2note = {'a': 'A3', 'b': 'B3', 'c': 'C4', 'd': 'D4', 'e': 'E4', 'f': 'F4', 'g': 'G4', 'h': 'A4', 'i': 'B4', 'j': 'C5', 
                'k': 'D5', 'l': 'E5', 'm': 'F5', 'n': 'G5', 'o': 'A5', 'p': 'B5', 'q': 'C6', 'r': 'D6', 's': 'E6', 't': 'F6'}

treble_note2code = {
    'A3': 'a', 'B3': 'b', 'C4': 'c', 'D4': 'd', 'E4': 'e', 'F4': 'f', 'G4': 'g',
    'A4': 'h', 'B4': 'i', 'C5': 'j', 'D5': 'k', 'E5': 'l', 'F5': 'm', 'G5': 'n',
    'A5': 'o', 'B5': 'p', 'C6': 'q', 'D6': 'r', 'E6': 's', 'F6': 't'
}

treble_code = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't']
treble_code2index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 
                     'l': 11, 'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17, 's': 18, 't': 19}


bass_code2note = {'A': 'A1', 'B': 'B1', 'C': 'C2', 'D': 'D2', 'E': 'E2', 'F': 'F2', 'G': 'G2', 'H': 'A2', 'I': 'B2', 'J': 
                     'C3', 'K': 'D3', 'L': 'E3', 'M': 'F3', 'N': 'G3', 'O': 'A3', 'P': 'B3', 'Q': 'C4', 'R': 'D4', 'S': 'E4', 'T': 'F4'}

bass_note2code = {
    'A1': 'A', 'B1': 'B', 'C2': 'C', 'D2': 'D', 'E2': 'E', 'F2': 'F', 'G2': 'G',
    'A2': 'H', 'B2': 'I', 'C3': 'J', 'D3': 'K', 'E3': 'L', 'F3': 'M', 'G3': 'N',
    'A3': 'O', 'B3': 'P', 'C4': 'Q', 'D4': 'R', 'E4': 'S', 'F4': 'T'
}

bass_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T']
bass_code2index = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9, 'K': 10, 
                   'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19}


chord_progressions_by_scale = {
    "Major": [
        [0, 4, 5],          # I-V-vi
        [0, 5, 3, 4],       # I-vi-IV-V
        [0, 4, 5, 3],       # I-V-vi-IV
        [0, 3, 4, 0],       # I-IV-V-I
        [0, 4, 0, 3, 4],    # I-V-I-IV-V
        [0, 5, 3, 4, 1, 0], # I-vi-IV-V-ii-I
        [0, 4, 5, 2, 3, 0, 3, 4],  # Pachelbel’s Canon: I-V-vi-iii-IV-I-IV-V
        [0, 4, 5, 2, 3, 0, 1, 4]   # Pachelbel’s Canon (variation): I-V-vi-iii-IV-I-ii-V
    ],
    "Dorian": [
        [0, 2, 4],          # i-ii-V
        [0, 5, 4, 2],       # i-V-IV-ii
        [0, 2, 4, 5],       # i-ii-V-i
        [0, 4, 5, 2, 0],    # i-V-VI-ii-i
        [0, 5, 3, 2, 4]     # i-V-IV-ii-V
    ],
    "Phrygian": [
        [0, 1, 4],          # i-bII-v
        [0, 3, 4, 5],       # i-iv-V-VI
        [0, 1, 4, 5],       # i-bII-v-VI
        [0, 5, 3, 4],       # i-VI-iv-V
        [0, 3, 1, 4, 5]     # i-iv-bII-v-VI
    ],
    "Lydian": [
        [0, 2, 5],          # I-II-V
        [0, 4, 2, 5],       # I-V-II-V
        [0, 5, 4, 2],       # I-V-IV-II
        [0, 2, 3, 4, 5],    # I-II-iii-IV-V
        [0, 5, 4, 3, 2]     # I-V-IV-iii-II
    ],
    "Mixolydian": [
        [0, 5, 4],          # I-V-IV
        [0, 4, 5, 3],       # I-IV-V-I
        [0, 5, 4, 3],       # I-V-IV-I
        [0, 3, 5, 4, 0],    # I-IV-V-I-V
        [0, 5, 3, 2, 4]     # I-V-ii-IV-V
    ],
    "Aeolian": [
        [0, 5, 3],          # i-VI-iv
        [0, 4, 5, 3],       # i-V-VI-iv
        [0, 5, 3, 4],       # i-VI-iv-V
        [0, 3, 5, 4, 0],    # i-iv-VI-V-i
        [0, 5, 4, 3, 1]     # i-VI-V-iv-bVII
    ],
    "Minor": [
        [0, 3, 4],          # i-iv-V
        [0, 5, 4, 3],       # i-VI-V-iv
        [0, 4, 5, 3],       # i-V-VI-iv
        [0, 5, 3, 2, 1],    # i-VI-iv-ii-bVII
        [0, 4, 2, 5, 3]     # i-V-ii-VI-iv
    ],
    "Locrian": [
        [0, 1, 3],          # i-bII-iv
        [0, 3, 4, 2],       # i-iv-v-ii
        [0, 4, 3, 1],       # i-v-iv-bII
        [0, 1, 4, 3, 2],    # i-bII-v-iv-ii
        [0, 3, 2, 1, 4]     # i-iv-ii-bII-v
    ],
    "Pentatonic Major": [
        [0, 2, 4],          # I-III-V
        [0, 3, 4, 2],       # I-IV-V-III
        [0, 4, 3, 2],       # I-V-IV-III
        [0, 2, 4, 3, 0],    # I-III-V-IV-I
        [0, 3, 4, 0, 2]     # I-IV-V-I-III
    ],
    "Pentatonic Minor": [
        [0, 3, 4],          # i-iv-v
        [0, 4, 2, 3],       # i-v-III-iv
        [0, 3, 4, 2],       # i-iv-v-III
        [0, 4, 3, 2, 0],    # i-v-iv-III-i
        [0, 2, 3, 4, 0]     # i-III-iv-v-i
    ]
}




