from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage
from fractions import Fraction
import json
import shutil
import subprocess
from pydub import AudioSegment
import os
os.system('clear')

NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'E#': 5, 'Fb': 4, 'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'B#': 0, 'Cb': 11
}

def note_to_midi(note):
    """Converts a note name (e.g., 'C4') to a MIDI note number."""
    if isinstance(note, list):  # Handle chords
        return [note_to_midi(n) for n in note]

    pitch, octave = note[:-1], int(note[-1])
    return (octave + 1) * 12 + NOTE_TO_MIDI[pitch]

def duration_to_ticks(duration, ticks_per_beat):
    """Converts a fraction duration to MIDI ticks."""
    return int(Fraction(duration) * ticks_per_beat * 4)  # Assuming 4/4 time

def json_to_midi(json_input, output_file="output.mid"):
    """
    Converts JSON-based music composition to a MIDI file with separate tracks for treble and bass.

    Args:
        json_input: The JSON dictionary (dict) representing the composition or the directory of the JSON dict.
        output_file (str): The filename for the generated MIDI file.
    """

    if isinstance(json_input, str):
        json_data = json.load(open(json_input, 'r'))
    else:
        json_data = json_input

    midi = MidiFile(ticks_per_beat=480)  # Standard ticks per beat
    treble_track = MidiTrack()
    bass_track = MidiTrack()
    midi.tracks.append(treble_track)
    midi.tracks.append(bass_track)

    # Set tempo (BPM to microseconds per beat)
    bpm = json_data.get("tempo", json_data['tempo'])  # Default to 120 BPM if not specified
    tempo = bpm2tempo(bpm)  # Convert BPM to microseconds per beat

    # Apply tempo to both tracks
    treble_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    bass_track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

    # Assign instruments (Piano by default, can be changed)
    treble_track.append(Message('program_change', program=0, time=0))  # Treble clef (track 1)
    bass_track.append(Message('program_change', program=0, time=0))  # Bass clef (track 2)

    ticks_per_beat = midi.ticks_per_beat

    for bar in json_data["bars"]:
        for clef, track in [("treble", treble_track), ("bass", bass_track)]:
            if clef not in bar["staves"]:
                continue  # Skip if no notes in clef

            for note_data in bar["staves"][clef]:
                midi_notes = note_to_midi(note_data["pitch"])
                ticks = duration_to_ticks(note_data["duration"], ticks_per_beat)

                if isinstance(midi_notes, list):  # Handle chords
                    for midi_note in midi_notes:
                        track.append(Message('note_on', note=midi_note, velocity=64, time=0))
                    for midi_note in midi_notes:
                        track.append(Message('note_off', note=midi_note, velocity=64, time=ticks))
                else:
                    track.append(Message('note_on', note=midi_notes, velocity=64, time=0))
                    track.append(Message('note_off', note=midi_notes, velocity=64, time=ticks))

    midi.save(output_file)
    # print(f"MIDI file saved as {output_file}")


def midi_to_mp3(midi_file, output_mp3="output.mp3", soundfont="soundfont/Yamaha_PSR-SX700_CP80.sf2"):
    """
    Converts a MIDI file to an MP3 file using FluidSynth.

    Args:
        midi_file (str): Path to the input MIDI file.
        output_mp3 (str, optional): Path to the output MP3 file.
        soundfont (str, optional): Path to the SF2 SoundFont file.

    Returns:
        str: Path to the generated MP3 file.
    """

    file_dir = os.path.dirname(output_mp3)
    output_wav = os.path.join(file_dir, "temp_output.wav")

    # Ensure FluidSynth is installed
    if not shutil.which("fluidsynth"):
        raise RuntimeError("FluidSynth is not installed. Install it via `sudo apt install fluidsynth` or `brew install fluidsynth`.")

    # Ensure SoundFont exists
    if not os.path.exists(soundfont):
        raise FileNotFoundError(f"SoundFont file '{soundfont}' not found.")
    
    # Determine null device (Windows: 'nul', Linux/macOS: '/dev/null')
    null_device = 'nul' if os.name == 'nt' else '/dev/null'

    # Convert MIDI to WAV using FluidSynth
    cmd = ["fluidsynth", "-ni", soundfont, midi_file, "-F", output_wav, "-r", "44100"]
    with open(null_device, 'w') as devnull:
        result = subprocess.run(cmd, stdout=devnull, stderr=devnull)
        # result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Debugging: Print any errors
    if result.returncode != 0:
        print("FluidSynth Error:", result.stderr.decode())
        raise RuntimeError("FluidSynth failed to generate WAV file.")

    # Ensure the WAV file was actually created
    if not os.path.exists(output_wav):
        raise FileNotFoundError("FluidSynth did not generate the WAV file.")

    # Convert WAV to MP3 using pydub
    audio = AudioSegment.from_wav(output_wav)
    audio.export(output_mp3, format="mp3")

    # Clean up temp WAV file
    os.remove(output_wav)

    # print(f"MP3 saved as {output_mp3}")
    return output_mp3


if __name__=='__main__':
    midi_to_mp3("music.mid", "music_output.mp3")