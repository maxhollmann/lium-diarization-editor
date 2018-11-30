import pandas as pd
from lium_diarization_editor import Diarization


def load_diarization(filename):
    with open(filename) as fp:
        lines = list(fp)
    lines = [l.strip().split(" ")
             for l in lines
             if not l.startswith(";;")]
    segs = pd.DataFrame(lines, columns=("show", "channel", "start", "length", "gender", "band", "environment", "speaker"))
    segs.start = pd.to_numeric(segs.start)
    segs.length = pd.to_numeric(segs.length)
    segs.sort_values('start', inplace=True)

    if 'original_speaker' not in segs:
        segs['original_speaker'] = segs['speaker']

    return Diarization(segments=segs)
