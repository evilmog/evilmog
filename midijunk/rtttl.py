#!/usr/bin/env python3
import re
import sys

def generate_midi_name_dict():
    """
    Returns a dict mapping all note names (with sharps and flats) to MIDI numbers,
    covering MIDI 0 (C-1) through MIDI 127 (G9).
    
    Example keys: 'c-1', 'c#-1', 'db-1', ..., 'g9', 'ab9'
    """
    sharp_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    flat_equivalents = {
        "C#": "Db",
        "D#": "Eb",
        "F#": "Gb",
        "G#": "Ab",
        "A#": "Bb",
    }

    name_to_midi = {}

    for midi_note in range(128):  # 0..127
        # octave = (midi_note // 12) - 1
        octave = (midi_note // 12) - 1
        pitch_class = midi_note % 12
        sharp_name = sharp_names[pitch_class]  # e.g. "C#", "D"
        note_sharp = f"{sharp_name}{octave}"   # e.g. "C#4"
        name_to_midi[note_sharp.lower()] = midi_note

        # If there's a flat equivalent, add that too
        if sharp_name in flat_equivalents:
            flat_name = flat_equivalents[sharp_name]
            note_flat = f"{flat_name}{octave}"
            name_to_midi[note_flat.lower()] = midi_note

    return name_to_midi


def rttl_to_midi_tuples(rttl_string, name_to_midi=None):
    """
    Parses an RTTTL string like:
      "MyTune:d=4,o=5,b=120:16g,8p,c6.,a"
    returning a list of (midi_note, duration_in_32nds).
    
    If name_to_midi is provided, it uses that for note lookups (covering sharps/flats).
    Otherwise, it will generate a basic partial dictionary for octave 4 only.
    """

    # If not provided, generate the full name->MIDI map
    # (But if you know you only need limited octaves, you could hard-code.)
    if name_to_midi is None:
        name_to_midi = generate_midi_name_dict()

    # 1) Split into sections: Name, defaults string (d=..., o=..., b=...), note sequence
    parts = rttl_string.strip().split(':', 2)
    if len(parts) < 3:
        raise ValueError("RTTTL string missing required ':' parts")

    tune_name = parts[0].strip()    # "MyTune"
    defs_part = parts[1].strip()    # "d=4,o=5,b=120"
    notes_str = parts[2].strip()    # "16g,8p,c6.,a"

    # 2) Parse the defaults (e.g. d=4, o=5, b=120)
    default_duration = 4
    default_octave = 5
    tempo = 120

    # We'll do quick regex searches for d=, o=, b=
    match_d = re.search(r'd\s*=\s*(\d+)', defs_part)
    match_o = re.search(r'o\s*=\s*(\d+)', defs_part)
    match_b = re.search(r'b\s*=\s*(\d+)', defs_part)

    if match_d:
        default_duration = int(match_d.group(1))
    if match_o:
        default_octave = int(match_o.group(1))
    if match_b:
        tempo = int(match_b.group(1))

    # RTTTL standard durations -> 32nd ticks
    duration_map = {
        1: 32,  # whole
        2: 16,  # half
        4: 8,   # quarter
        8: 4,   # eighth
        16: 2,  # sixteenth
        32: 1   # thirty-second
    }
    default_dur_32 = duration_map.get(default_duration, 8)

    # 3) Parse the notes (comma-separated)
    tokens = [x.strip().lower() for x in notes_str.split(',')]
    result = []

    for token in tokens:
        # Pattern: optional digits (duration), note/rest (a-g or p), optional #/b, optional octave, optional dot (.)
        # Example: "16g", "4p", "a6.", "8c#6", "c6.", "2f#."
        m = re.match(r'^(\d*)'      # optional leading duration
                     r'([a-gp])'    # note letter or 'p'
                     r'(#|b)?'      # optional sharp(#) or flat(b)
                     r'(\d*)'       # optional octave
                     r'(\.)?',      # optional dotted
                     token, re.IGNORECASE)

        if not m:
            raise ValueError(f"Unrecognized token: {token}")

        dur_str, note_char, accidental, octave_str, dot_str = m.groups()

        # A) duration in 32nds
        if dur_str:
            dur_val = int(dur_str)
            base_dur_32 = duration_map.get(dur_val, 8)
        else:
            base_dur_32 = default_dur_32

        is_dotted = (dot_str == '.')
        if is_dotted:
            # dotted => multiply by 1.5 => must be integer after that
            base_dur_32 = int(base_dur_32 * 1.5)

        # B) octave
        if octave_str:
            octave = int(octave_str)
        else:
            octave = default_octave

        # C) pitch
        if note_char == 'p':
            # rest
            midi_note = 0
        else:
            # e.g. note_char='g' + accidental='#' => "g#"
            full_note_name = note_char
            if accidental:
                full_note_name += accidental
            # e.g. "g#" => "g#4" => "g#4"
            full_note_name += str(octave)

            if full_note_name not in name_to_midi:
                raise ValueError(f"Note name not found in dictionary: {full_note_name}")
            midi_note = name_to_midi[full_note_name]

        result.append((midi_note, base_dur_32))

    return result, tune_name, default_duration, default_octave, tempo


def make_circuitpython_snippet(rttl_string):
    """
    Generates a Python snippet assigning the parsed RTTTL as
    a list of (midi_note, duration_in_32nds).
    
    Example usage:
        snippet = make_circuitpython_snippet("Wannabe:d=4,o=5,b=125:...")
        print(snippet)
    """
    name_to_midi = generate_midi_name_dict()
    parsed, tune_name, d, o, b = rttl_to_midi_tuples(rttl_string, name_to_midi)

    # Build a Python code snippet
    # We'll use a variable named from the tune_name, but sanitized for code
    var_name = tune_name.lower().replace(" ", "_").replace("-", "_")
    lines = [f"{var_name}_melody = ["]

    for (note, dur) in parsed:
        lines.append(f"    ({note}, {dur}),")

    lines.append("]")
    return "\n".join(lines)


def main():
    # If you run the script with an RTTTL string as an argument, e.g.:
    #   python rttl_to_circuitpython.py "Wannabe:d=4,o=5,b=125:16g,16g,..."
    # it will print the snippet.
    if len(sys.argv) < 2:
        print("Usage: python rttl_to_circuitpython.py \"<RTTTL_STRING>\"")
        print("Example:")
        print("   python rttl_to_circuitpython.py \"Wannabe:d=4,o=5,b=125:16g,16g,16g...\"")
        sys.exit(1)

    rttl_input = sys.argv[1]
    snippet = make_circuitpython_snippet(rttl_input)
    print("Generated CircuitPython snippet:\n")
    print(snippet)


if __name__ == "__main__":
    main()
