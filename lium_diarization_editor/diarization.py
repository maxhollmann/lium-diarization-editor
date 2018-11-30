import os

import warnings

import numpy as np
import pandas as pd



class Diarization:
    def __init__(self, segments, frame_size = 10):
        self.segs = segments
        self.frame_size = frame_size

        # Calculate some useful things
        self.num_segments = self.segs.shape[0]

        last = self.segs.iloc[self.num_segments - 1]
        self.estimated_total_frames = last.start + last.length

        self.speakers = np.unique(self.segs.speaker)
        self.num_speakers = self.speakers.shape[0]


    def iter_segments(self):
        return self.segs.iterrows()

    def segment_at(self, i):
        return self.segs.iloc[i]


    def change_speaker(self, speaker, new_name):
        new_segs = self.segs.copy()
        new_segs.loc[self.segs.speaker == speaker, "speaker"] = new_name
        return self.update_segs(new_segs)


    def merge_equal_neighbors(self):
        """ Merge neighbors with same speaker. """
        IDX_LENGTH = 3

        merged = self.segs.copy()
        current_start = 0
        j = 0
        seg = self.segs.iloc[0]
        for i in range(1, self.num_segments):
            seg = self.segs.iloc[i]
            last = self.segs.iloc[i - 1]
            if seg.speaker == last.speaker:
                merged.iat[j, IDX_LENGTH] = seg.start + seg.length - current_start
            else:
                j += 1
                merged.iloc[j] = seg
                current_start = seg.start
        merged = merged.iloc[:(j+1)]
        merged.sort_values('start', inplace = True)

        return self.update_segs(merged)

    def update_segs(self, new_segs):
        return Diarization(segments = new_segs,
                           frame_size = self.frame_size)


    def frame_to_time(self, frame):
        return frame * self.frame_size



    def save(self, filename):
        self.segs.to_pickle(filename)

    @classmethod
    def load(cls, filename):
        segs = pd.read_pickle(filename)
        return Diarization(segments = segs)
