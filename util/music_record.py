from fractions import Fraction
from typing import List
import json
from util.note_mapping import treble_code2note, bass_code2note
from util.MIDI_util import json_to_midi, midi_to_mp3
from util.scale_util import get_note_accidentals
import os
os.system('clear')

note_split_dict = {1: [1], 2: [2], 3: [3], 4: [4], 5: [4, 1], 
                 6: [6], 7: [7], 8: [8], 9: [8, 1], 
                 10: [8, 2], 11: [8, 3], 
                 12: [12], 13: [12, 1], 14: [14], 
                 15: [12, 3], 16: 16}

def get_beat_tie_list(n, beat_tie, split='note'):
        out = [False for _ in range(n)]
        if beat_tie == 0:
            return out
        elif split=='note':
            out[0] = True
            return out
        elif split=='beat':
            out[-1] = True
            return out

        
def beat_split_note(tempo_list, pitch_list):

    tempo_list_mod = [note_split_dict[x] for x in tempo_list]
    pitch_list_mod = [[x] * len(y) for x, y in zip(pitch_list, tempo_list_mod)]
    connect_list = [get_beat_tie_list(len(y), len(y)!=1, split='note') for x, y in zip(pitch_list, tempo_list_mod)]

    tempo_list = sum(tempo_list_mod, [])
    pitch_list = sum(pitch_list_mod, [])
    connect_list = sum(connect_list, [])
    return tempo_list, pitch_list, connect_list


def beat_split_beat(tempo_list, pitch_list, beat_len=4):
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

    # strech list of lists to single list
    connect_list = [get_beat_tie_list(len(beat_len), beat_tie, split='beat') for beat_len, beat_tie in zip(beat_len_list, connect_list)]
    beat_len_list = sum(beat_len_list, [])
    beat_pitch_list = sum(beat_pitch_list, [])
    connect_list = sum(connect_list, [])


    return beat_len_list, beat_pitch_list, connect_list


class Note:
    """Represents a single musical note or chord."""
    def __init__(self, pitch, duration, tie=False):
        """
        Args:
            pitch (str or list): Single note (e.g., "C4") or chord (list of notes).
            duration (str): Note duration (e.g., "1/4", "1/8").
            tie (str, optional): "start" or "continue" if the note is tied.
        """
        self.pitch = pitch
        self.duration = duration
        self.tie = tie  # Optional tie field

    def to_dict(self):
        """Converts the Note object to a dictionary."""
        note_data = {"pitch": self.pitch, "duration": self.duration}
        if self.tie:
            note_data["tie"] = self.tie
        
        return note_data

    def __str__(self):
        """String representation of a Note object."""
        tie_str = f", tie={self.tie}" if self.tie else ""
        return f"Note(pitch={self.pitch}, duration={self.duration}{tie_str})"


class BarMusic:
    """Represents a measure (bar) in sheet music with treble and bass staves."""
    def __init__(self, bar_number, chord=None, repeat_start=False, repeat_end=False):
        """
        Args:
            bar_number (int): The measure number in the piece.
        """
        self.bar_number = bar_number
        self.repeat_start = repeat_start
        self.repeat_end = repeat_end
        self.chord = chord
        self.staves = {"treble": [], "bass": []}  # Holds notes for each clef

    def add_note(self, clef, note):
        """
        Adds a note or chord to the specified clef.
        
        Args:
            clef (str): "treble" or "bass".
            note (Note): A Note object.
        """
        if clef not in self.staves:
            raise ValueError("Invalid clef. Choose 'treble' or 'bass'.")
        self.staves[clef].append(note)

    def to_dict(self):
        """Converts the BarMusic object to a dictionary for JSON serialization."""
        bar_dict = {"bar_number": self.bar_number, 'chord': self.chord}
        
        # Add repeat markers if present
        if self.repeat_start or self.repeat_end:
            bar_dict["repeat"] = "start" if self.repeat_start else "end"

        # Add staves only if they contain notes
        staves = {clef: [note.to_dict() for note in self.staves[clef]] 
                for clef in ("treble", "bass") if self.staves[clef]}
        
        if staves:
            bar_dict["staves"] = staves

        return bar_dict


    def __str__(self):
        """String representation of a BarMusic object."""
        staves = {clef: ", ".join(str(note) for note in self.staves[clef]) 
                for clef in ("treble", "bass") if self.staves[clef]}

        rep_str = f"Bar {self.bar_number}:"
        if "treble" in staves:
            rep_str += f"\n  Treble: [{staves['treble']}]"
        if "bass" in staves:
            rep_str += f"\n  Bass: [{staves['bass']}]"

        return rep_str

class MusicComposition:
    """Represents a full music composition with tempo, key, and bars."""
    def __init__(self, tempo=120, key="C Major", time_signature="4/4"):
        """
        Args:
            tempo (int): Beats per minute.
            key (str): Key signature (e.g., "C Major").
            time_signature (str): Time signature (e.g., "4/4").
        """
        self.tempo = int(tempo)
        self.key = key
        self.scale_root = key.split(' ')[0]
        self.scale_type = key.split(' ')[1]
        self.time_signature = time_signature
        self.bars: List[BarMusic] = []

    def add_bar(self, bar):
        """
        Adds a BarMusic object to the composition.

        Args:
            bar (BarMusic): The bar (measure) object.
        """
        self.bars.append(bar)

    def to_dict(self):
        """Converts the MusicComposition object to a dictionary."""
        return {
            "tempo": self.tempo,
            "key": self.key,
            "time_signature": self.time_signature,
            "bars": [bar.to_dict() for bar in self.bars]
        }

    def to_json(self, file_dir, file_name='music'):
        """Saves the composition as a JSON file."""
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        filename = os.path.join(file_dir, f'{file_name}.json')
        
        with open(filename, "w") as json_file:
            json.dump(self.to_dict(), json_file, indent=2)
        # print(f"Music composition saved to {filename}")

    def to_midi(self, file_dir, audio=False, file_name='music'):
        json_input = self.to_dict()
        filename = os.path.join(file_dir, f'{file_name}.mid')
        json_to_midi(json_input, filename)

        if audio:
            midi_to_mp3(filename, os.path.join(file_dir, f'{file_name}.mp3'))


    def __str__(self):
        """String representation of a MusicComposition object."""
        bars_str = "\n".join(str(bar) for bar in self.bars)
        return f"MusicComposition:\n  Tempo: {self.tempo} BPM\n  Key: {self.key}\n  Time Signature: {self.time_signature}\n{bars_str}"
    

    def record_bar(self, bar_number, chord=None, treble_tempo_list=None, treble_pitch_list=None, 
                   bass_tempo_list=None, bass_pitch_list=None, encode_format='beat'):
        """
        Stores notes in a bar for treble and/or bass clefs with independent tempos.

        Args:
            bar_number (int): The measure number.
            treble_tempo_list (list, optional): Durations for treble clef notes.
            treble_pitch_list (list, optional): Pitches for the treble clef.
            bass_tempo_list (list, optional): Durations for bass clef notes.
            bass_pitch_list (list, optional): Pitches for the bass clef.

        Returns:
            BarMusic: An instance of BarMusic containing the stored notes.
        """
        bar = BarMusic(bar_number, chord)

        # Add treble notes with independent durations
        if treble_tempo_list and treble_pitch_list:
            treble_pitch_list = [treble_code2note[x] for x in treble_pitch_list]
            treble_pitch_list = [get_note_accidentals(self.scale_type, self.scale_root, x) for x in treble_pitch_list]

            if encode_format == 'beat':
                treble_tempo_list, treble_pitch_list, connect_list = beat_split_beat(treble_tempo_list, treble_pitch_list)
            else:
                treble_tempo_list, treble_pitch_list, connect_list = beat_split_note(treble_tempo_list, treble_pitch_list)
                
            for i in range(min(len(treble_tempo_list), len(treble_pitch_list))):
                bar.add_note("treble", Note(treble_pitch_list[i], str(Fraction(treble_tempo_list[i], 16)), connect_list[i]))

        # Add bass notes with independent durations
        if bass_tempo_list and bass_pitch_list:
            bass_pitch_list = [bass_code2note[x] for x in bass_pitch_list]
            bass_pitch_list = [get_note_accidentals(self.scale_type, self.scale_root, x) for x in bass_pitch_list]

            if encode_format == 'beat':
                bass_tempo_list, bass_pitch_list, connect_list = beat_split_beat(bass_tempo_list, bass_pitch_list)
            else:
                bass_tempo_list, bass_pitch_list, connect_list = beat_split_note(bass_tempo_list, bass_pitch_list)

            for i in range(min(len(bass_tempo_list), len(bass_pitch_list))):
                bar.add_note("bass", Note(bass_pitch_list[i], str(Fraction(bass_tempo_list[i], 16)), connect_list[i]))

        self.add_bar(bar)
        return bar

