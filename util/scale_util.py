import os

scale_types = ["Major", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Minor",
              "Locrian", "Pentatonic Major", "Pentatonic Minor"]

scales_dict = {
    "Major": {
        "C": ["C", "D", "E", "F", "G", "A", "B"],
        "G": ["G", "A", "B", "C", "D", "E", "F#"],
        "D": ["D", "E", "F#", "G", "A", "B", "C#"],
        "A": ["A", "B", "C#", "D", "E", "F#", "G#"],
        "E": ["E", "F#", "G#", "A", "B", "C#", "D#"],
        "B": ["B", "C#", "D#", "E", "F#", "G#", "A#"],
        "F#": ["F#", "G#", "A#", "B", "C#", "D#", "E#"],
        "C#": ["C#", "D#", "E#", "F#", "G#", "A#", "B#"],
        "F": ["F", "G", "A", "Bb", "C", "D", "E"],
        "Bb": ["Bb", "C", "D", "Eb", "F", "G", "A"],
        "Eb": ["Eb", "F", "G", "Ab", "Bb", "C", "D"],
        "Ab": ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],
        "Db": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"],
        "Gb": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],
        "Cb": ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],
    },
    "Dorian": {
        "C": ["C", "D", "Eb", "F", "G", "A", "Bb"],
        "G": ["G", "A", "Bb", "C", "D", "E", "F"],
        "D": ["D", "E", "F", "G", "A", "B", "C"],
        "A": ["A", "B", "C", "D", "E", "F#", "G"],
        "E": ["E", "F#", "G", "A", "B", "C#", "D"],
        "B": ["B", "C#", "D", "E", "F#", "G#", "A"],
        "F#": ["F#", "G#", "A", "B", "C#", "D#", "E"],
        "C#": ["C#", "D#", "E", "F#", "G#", "A#", "B"],
        "F": ["F", "G", "Ab", "Bb", "C", "D", "Eb"],
        "Bb": ["Bb", "C", "Db", "Eb", "F", "G", "Ab"],
        "Eb": ["Eb", "F", "Gb", "Ab", "Bb", "C", "Db"],
        "Ab": ["Ab", "Bb", "Cb", "Db", "Eb", "F", "Gb"],
        "Db": ["Db", "Eb", "Fb", "Gb", "Ab", "Bb", "Cb"],
        "Gb": ["Gb", "Ab", "Bbb", "Cb", "Db", "Eb", "Fb"],
        "Cb": ["Cb", "Db", "Ebb", "Fb", "Gb", "Ab", "Bbb"],
    },
    "Phrygian": {
        "C": ["C", "Db", "Eb", "F", "G", "Ab", "Bb"],
        "G": ["G", "Ab", "Bb", "C", "D", "Eb", "F"],
        "D": ["D", "Eb", "F", "G", "A", "Bb", "C"],
        "A": ["A", "Bb", "C", "D", "E", "F", "G"],
        "E": ["E", "F", "G", "A", "B", "C", "D"],
        "B": ["B", "C", "D", "E", "F#", "G", "A"],
        "F#": ["F#", "G", "A", "B", "C#", "D", "E"],
        "C#": ["C#", "D", "E", "F#", "G#", "A", "B"],
        "F": ["F", "Gb", "Ab", "Bb", "C", "Db", "Eb"],
        "Bb": ["Bb", "Cb", "Db", "Eb", "F", "Gb", "Ab"],
        "Eb": ["Eb", "Fb", "Gb", "Ab", "Bb", "Cb", "Db"],
        "Ab": ["Ab", "Bbb", "Cb", "Db", "Eb", "Fb", "Gb"],
        "Db": ["Db", "Ebb", "Fb", "Gb", "Ab", "Bbb", "Cb"],
        "Gb": ["Gb", "Abb", "Bbb", "Cb", "Db", "Ebb", "Fb"],
        "Cb": ["Cb", "Dbb", "Ebb", "Fb", "Gb", "Abb", "Bbb"],
    },
    "Lydian": {
        "C": ["C", "D", "E", "F#", "G", "A", "B"],
        "G": ["G", "A", "B", "C#", "D", "E", "F#"],
        "D": ["D", "E", "F#", "G#", "A", "B", "C#"],
        "A": ["A", "B", "C#", "D#", "E", "F#", "G#"],
        "E": ["E", "F#", "G#", "A#", "B", "C#", "D#"],
        "B": ["B", "C#", "D#", "E#", "F#", "G#", "A#"],
        "F#": ["F#", "G#", "A#", "B#", "C#", "D#", "E#"],
        "C#": ["C#", "D#", "E#", "F##", "G#", "A#", "B#"],
        "F": ["F", "G", "A", "B", "C", "D", "E"],
        "Bb": ["Bb", "C", "D", "E", "F", "G", "A"],
        "Eb": ["Eb", "F", "G", "A", "Bb", "C", "D"],
        "Ab": ["Ab", "Bb", "C", "D", "Eb", "F", "G"],
        "Db": ["Db", "Eb", "F", "G", "Ab", "Bb", "C"],
        "Gb": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],
        "Cb": ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],
    },
    "Mixolydian": {
        "C": ["C", "D", "E", "F", "G", "A", "Bb"],
        "G": ["G", "A", "B", "C", "D", "E", "F"],
        "D": ["D", "E", "F#", "G", "A", "B", "C"],
        "A": ["A", "B", "C#", "D", "E", "F#", "G"],
        "E": ["E", "F#", "G#", "A", "B", "C#", "D"],
        "B": ["B", "C#", "D#", "E", "F#", "G#", "A"],
        "F#": ["F#", "G#", "A#", "B", "C#", "D#", "E"],
        "C#": ["C#", "D#", "E#", "F#", "G#", "A#", "B"],
        "F": ["F", "G", "A", "Bb", "C", "D", "Eb"],
        "Bb": ["Bb", "C", "D", "Eb", "F", "G", "Ab"],
        "Eb": ["Eb", "F", "G", "Ab", "Bb", "C", "Db"],
        "Ab": ["Ab", "Bb", "C", "Db", "Eb", "F", "Gb"],
        "Db": ["Db", "Eb", "F", "Gb", "Ab", "Bb", "Cb"],
        "Gb": ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "Fb"],
        "Cb": ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],
    },
    "Aeolian": {
        "A": ["A", "B", "C", "D", "E", "F", "G"],
        "E": ["E", "F#", "G", "A", "B", "C", "D"],
        "B": ["B", "C#", "D", "E", "F#", "G", "A"],
        "F#": ["F#", "G#", "A", "B", "C#", "D", "E"],
        "C#": ["C#", "D#", "E", "F#", "G#", "A", "B"],
        "G#": ["G#", "A#", "B", "C#", "D#", "E", "F#"],
        "D#": ["D#", "E#", "F#", "G#", "A#", "B", "C#"],
        "A#": ["A#", "B#", "C#", "D#", "E#", "F#", "G#"],
        "D": ["D", "E", "F", "G", "A", "Bb", "C"],
        "G": ["G", "A", "Bb", "C", "D", "Eb", "F"],
        "C": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
        "F": ["F", "G", "Ab", "Bb", "C", "Db", "Eb"],
        "Bb": ["Bb", "C", "Db", "Eb", "F", "Gb", "Ab"],
        "Eb": ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "Db"],
        "Ab": ["Ab", "Bb", "Cb", "Db", "Eb", "Fb", "Gb"],
    },
    "Locrian": {
        "B": ["B", "C", "D", "E", "F", "G", "A"],
        "F#": ["F#", "G", "A", "B", "C", "D", "E"],
        "C#": ["C#", "D", "E", "F#", "G", "A", "B"],
        "G#": ["G#", "A", "B", "C#", "D", "E", "F#"],
        "D#": ["D#", "E", "F#", "G#", "A", "B", "C#"],
        "A#": ["A#", "B", "C#", "D#", "E", "F#", "G#"],
        "E#": ["E#", "F#", "G#", "A#", "B", "C#", "D#"],
        "B#": ["B#", "C#", "D#", "E#", "F#", "G#", "A#"],
        "F": ["F", "Gb", "Ab", "Bb", "Cb", "Db", "Eb"],
        "C": ["C", "Db", "Eb", "F", "Gb", "Ab", "Bb"],
        "G": ["G", "Ab", "Bb", "C", "Db", "Eb", "F"],
        "D": ["D", "Eb", "F", "G", "Ab", "Bb", "C"],
        "A": ["A", "Bb", "C", "D", "Eb", "F", "G"],
        "E": ["E", "F", "G", "A", "Bb", "C", "D"],
        "Bb": ["Bb", "Cb", "Db", "Eb", "Fb", "Gb", "Ab"],
    },
    "Pentatonic Major": {
        "C": ["C", "D", "E", "G", "A"],
        "G": ["G", "A", "B", "D", "E"],
        "D": ["D", "E", "F#", "A", "B"],
        "A": ["A", "B", "C#", "E", "F#"],
        "E": ["E", "F#", "G#", "B", "C#"],
        "B": ["B", "C#", "D#", "F#", "G#"],
        "F#": ["F#", "G#", "A#", "C#", "D#"],
        "C#": ["C#", "D#", "E#", "G#", "A#"],
        "F": ["F", "G", "A", "C", "D"],
        "Bb": ["Bb", "C", "D", "F", "G"],
        "Eb": ["Eb", "F", "G", "Bb", "C"],
        "Ab": ["Ab", "Bb", "C", "Eb", "F"],
        "Db": ["Db", "Eb", "F", "Ab", "Bb"],
        "Gb": ["Gb", "Ab", "Bb", "Db", "Eb"],
        "Cb": ["Cb", "Db", "Eb", "Gb", "Ab"],
    },
    "Pentatonic Minor": {
        "A": ["A", "C", "D", "E", "G"],
        "E": ["E", "G", "A", "B", "D"],
        "B": ["B", "D", "E", "F#", "A"],
        "F#": ["F#", "A", "B", "C#", "E"],
        "C#": ["C#", "E", "F#", "G#", "B"],
        "G#": ["G#", "B", "C#", "D#", "F#"],
        "D#": ["D#", "F#", "G#", "A#", "C#"],
        "A#": ["A#", "C#", "D#", "F", "G#"],
        "D": ["D", "F", "G", "A", "C"],
        "G": ["G", "Bb", "C", "D", "F"],
        "C": ["C", "Eb", "F", "G", "Bb"],
        "F": ["F", "Ab", "Bb", "C", "Eb"],
        "Bb": ["Bb", "Db", "Eb", "F", "Ab"],
        "Eb": ["Eb", "Gb", "Ab", "Bb", "Db"],
        "Ab": ["Ab", "Cb", "Db", "Eb", "Gb"],
    },
    "Minor": {
        "A": ["A", "B", "C", "D", "E", "F", "G"],
        "E": ["E", "F#", "G", "A", "B", "C", "D"],
        "B": ["B", "C#", "D", "E", "F#", "G", "A"],
        "F#": ["F#", "G#", "A", "B", "C#", "D", "E"],
        "C#": ["C#", "D#", "E", "F#", "G#", "A", "B"],
        "G#": ["G#", "A#", "B", "C#", "D#", "E", "F#"],
        "D#": ["D#", "E#", "F#", "G#", "A#", "B", "C#"],
        "A#": ["A#", "B#", "C#", "D#", "E#", "F#", "G#"],
        "D": ["D", "E", "F", "G", "A", "Bb", "C"],
        "G": ["G", "A", "Bb", "C", "D", "Eb", "F"],
        "C": ["C", "D", "Eb", "F", "G", "Ab", "Bb"],
        "F": ["F", "G", "Ab", "Bb", "C", "Db", "Eb"],
        "Bb": ["Bb", "C", "Db", "Eb", "F", "Gb", "Ab"],
        "Eb": ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "Db"],
        "Ab": ["Ab", "Bb", "Cb", "Db", "Eb", "Fb", "Gb"],
    },
    "Harmonic Minor": {
        "A": ["A", "B", "C", "D", "E", "F", "G#"],
        "E": ["E", "F#", "G", "A", "B", "C", "D#"],
        "B": ["B", "C#", "D", "E", "F#", "G", "A#"],
        "F#": ["F#", "G#", "A", "B", "C#", "D", "E#"],
        "C#": ["C#", "D#", "E", "F#", "G#", "A", "B#"],
        "G#": ["G#", "A#", "B", "C#", "D#", "E", "Fx"],
        "D#": ["D#", "E#", "F#", "G#", "A#", "B", "Cx"],
        "A#": ["A#", "B#", "C#", "D#", "E#", "F#", "Gx"],
        "D": ["D", "E", "F", "G", "A", "Bb", "C#"],
        "G": ["G", "A", "Bb", "C", "D", "Eb", "F#"],
        "C": ["C", "D", "Eb", "F", "G", "Ab", "B"],
        "F": ["F", "G", "Ab", "Bb", "C", "Db", "E"],
        "Bb": ["Bb", "C", "Db", "Eb", "F", "Gb", "A"],
        "Eb": ["Eb", "F", "Gb", "Ab", "Bb", "Cb", "D"],
        "Ab": ["Ab", "Bb", "Cb", "Db", "Eb", "Fb", "G"],
    },
    "Melodic Minor": {
        "A": ["A", "B", "C", "D", "E", "F#", "G#"],
        "E": ["E", "F#", "G", "A", "B", "C#", "D#"],
        "B": ["B", "C#", "D", "E", "F#", "G#", "A#"],
        "F#": ["F#", "G#", "A", "B", "C#", "D#", "E#"],
        "C#": ["C#", "D#", "E", "F#", "G#", "A#", "B#"],
        "G#": ["G#", "A#", "B", "C#", "D#", "E#", "Fx"],
        "D#": ["D#", "E#", "F#", "G#", "A#", "B#", "Cx"],
        "A#": ["A#", "B#", "C#", "D#", "E#", "Fx", "Gx"],
        "D": ["D", "E", "F", "G", "A", "B", "C#"],
        "G": ["G", "A", "Bb", "C", "D", "E", "F#"],
        "C": ["C", "D", "Eb", "F", "G", "A", "B"],
        "F": ["F", "G", "Ab", "Bb", "C", "D", "E"],
        "Bb": ["Bb", "C", "Db", "Eb", "F", "G", "A"],
        "Eb": ["Eb", "F", "Gb", "Ab", "Bb", "C", "D"],
        "Ab": ["Ab", "Bb", "Cb", "Db", "Eb", "F", "G"],
    }
}

chord_types = {
    "Major": ["Major", "Minor", "Minor", "Major", "Major", "Minor", "Diminished"],
    "Dorian": ["Minor", "Minor", "Major", "Major", "Minor", "Diminished", "Major"],
    "Phrygian": ["Minor", "Major", "Major", "Minor", "Diminished", "Major", "Minor"],
    "Lydian": ["Major", "Major", "Minor", "Diminished", "Major", "Minor", "Minor"],
    "Mixolydian": ["Major", "Minor", "Diminished", "Major", "Minor", "Minor", "Major"],
    "Aeolian": ["Minor", "Diminished", "Major", "Minor", "Minor", "Major", "Major"],
    "Minor": ["Minor", "Diminished", "Major", "Minor", "Minor", "Major", "Major"],
    "Locrian": ["Diminished", "Major", "Minor", "Minor", "Major", "Major", "Minor"],
    "Pentatonic Major": ["Major", "Major", "Minor", "Minor", "Major"],
    "Pentatonic Minor": ["Minor", "Minor", "Major", "Major", "Minor"],
    "Melodic Minor": ["Minor", "Minor", "Augmented", "Major", "Major", "Diminished", "Diminished"],
    "Harmonic Minor": ["Minor", "Diminished", "Augmented", "Minor", "Major", "Major", "Diminished"]
}

symbol_translate = {'Major': '', 'Minor': 'm', 'Diminished': 'dim', 'Augmented': 'aug'}

def get_chord_notes(scale_notes, chord_index):
    
    # Intervals within the scale for triads, using scale degrees
    chord_intervals = [0, 2, 4]
    
    # Determine the root index of the chord within the scale
    root_index = (chord_index - 1) % len(scale_notes)  # wrap if needed
    
    # Collect the chord notes based on the intervals
    chord_notes = []
    for interval in chord_intervals:
        note_index = (root_index + interval) % len(scale_notes)
        chord_notes.append(scale_notes[note_index])
    
    return chord_notes


def get_chord_symbol(scale_type, scale_root, chord_index):

    chord_type = symbol_translate[chord_types[scale_type][chord_index-1]]
    chord_root = scales_dict[scale_type][scale_root][chord_index-1]

    chord_root = chord_root.replace('#', '\#')

    return f'{chord_root}{chord_type}'


def get_note_accidentals(scale_type, scale_root, note):

    scale = scales_dict.get(scale_type, {}).get(scale_root, [])

    for note_in_scale in scale:
        if note[0] == note_in_scale[0]:
            return note.replace(note[0], note_in_scale)
    return note



scale_key_signatures = {
    0: ["C", "D", "E", "F", "G", "A", "B"],  # C Major
    1: ["G", "A", "B", "C", "D", "E", "F#"],  # G Major
    2: ["D", "E", "F#", "G", "A", "B", "C#"],  # D Major
    3: ["A", "B", "C#", "D", "E", "F#", "G#"],  # A Major
    4: ["E", "F#", "G#", "A", "B", "C#", "D#"],  # E Major
    5: ["B", "C#", "D#", "E", "F#", "G#", "A#"],  # B Major
    6: ["F#", "G#", "A#", "B", "C#", "D#", "E#"],  # F# Major
    7: ["C#", "D#", "E#", "F#", "G#", "A#", "B#"],  # C# Major
    -1: ["F", "G", "A", "Bb", "C", "D", "E"],  # F Major
    -2: ["Bb", "C", "D", "Eb", "F", "G", "A"],  # Bb Major
    -3: ["Eb", "F", "G", "Ab", "Bb", "C", "D"],  # Eb Major
    -4: ["Ab", "Bb", "C", "Db", "Eb", "F", "G"],  # Ab Major
    -5: ["Db", "Eb", "F", "Gb", "Ab", "Bb", "C"],  # Db Major
    -6: ["Gb", "Ab", "Bb", "Cb", "Db", "Eb", "F"],  # Gb Major
    -7: ["Cb", "Db", "Eb", "Fb", "Gb", "Ab", "Bb"],  # Cb Major
}