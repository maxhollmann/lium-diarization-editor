# requires python-mpv

import numpy as np

from threading import Lock

import matplotlib.pyplot as plt
import matplotlib.patches as patches

import os
from datetime import datetime
import math


class DiarizationEditor:
    def __init__(self, diarization, player = None, save_path=None, save_latest_path=None):
        self.diarization = diarization
        self.merged_dia = diarization.merge_equal_neighbors()
        self.player = player
        self.save_path = save_path
        self.save_latest_path = save_latest_path
        self._update_history = []
        self._limited_to_speaker = None
        self._seek_to_speaker_lock = Lock()


        self.total_frames = self.diarization.estimated_total_frames

        if player:
            tf_from_audio = math.floor(player.length / self.diarization.frame_size)
            if abs(self.total_frames - tf_from_audio) * self.diarization.frame_size > 1000:
                print("Total frames calculated from segments and audio length differ: {} vs {}".
                      format(self.total_frames, tf_from_audio))
            self.total_frames = tf_from_audio


    def run(self):
        speakers = self.diarization.speakers
        speakers.sort()
        self.speakers = speakers

        disabled_matplotlib_keys = (
            's', 'l', 'p', 'n', 'm', '?', 'space', 'left', 'right', 'u', 'home',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        )
        for key, val in plt.rcParams.items():
            if not key.startswith("keymap."): continue
            if any([k in disabled_matplotlib_keys for k in val]):
                plt.rcParams[key] = ''

        fig = plt.figure()
        ax_seg = fig.add_subplot(111)

        self.fig = fig
        self.ax_seg = ax_seg

        ax_seg.set_xlim(0, self.total_frames)
        ax_seg.set_ylim(-0.5, self.diarization.num_speakers + 0.5)

        colors = plt.cm.Set1(np.linspace(0, 1, self.diarization.num_speakers))
        color_map = {}
        y_map = {}
        for i, speaker in enumerate(speakers):
            color_map[speaker] = colors[i]
            y_map[speaker] = i

        self._set_yticklabels()

        for i, seg in self.diarization.iter_segments():
            ax_seg.add_patch(
                patches.Rectangle(
                    (seg.start, y_map[seg.speaker] - 0.4),
                    seg.length, 0.8,
                    facecolor = color_map[seg.speaker],
                    edgecolor = 'none'
                )
            )


        if self.player:
            self._setup_player()
            self.player.observe_position(self._on_player_position_change)

        plt.show()

    def close(self):
        for cid in self.conn_ids:
            self.fig.canvas.mpl_disconnect(cid)
        plt.close('all')


    def _set_yticklabels(self):
        speakers = np.array(self.speakers)
        if self._limited_to_speaker:
            speakers = np.where(speakers == self._limited_to_speaker,
                                "==> {}".format(self._limited_to_speaker),
                                speakers)
        self.ax_seg.set_yticks(np.arange(len(speakers)))
        self.ax_seg.set_yticklabels(speakers)


    def _setup_player(self):
        self.playhead = self.ax_seg.axvline(0)

        timer = self.fig.canvas.new_timer(interval=500)
        timer.add_callback(self._update_playhead)
        timer.start()


        self.conn_ids = [
            self.fig.canvas.mpl_connect('button_press_event', self._on_click),
            self.fig.canvas.mpl_connect('key_press_event', self._on_keypress)
        ]


    def _limit_to_speaker(self, speaker):
        self._limited_to_speaker = speaker
        self._set_yticklabels()


    def _current_frame(self):
        frame = self.total_frames * self.player.progress()
        return frame

    def _segment_index_at_frame(self, frame):
        for i in range(self.merged_dia.num_segments):
            seg = self.merged_dia.segment_at(i)
            if seg.start + seg.length > frame:
                return i

    def _seek_to_frame(self, frame):
        self.player.seek_progress(frame / self.total_frames)

    def _update_playhead(self):
        x = self._current_frame()
        self.playhead.set_xdata(x)
        self.playhead.figure.canvas.draw()



    def _on_player_position_change(self, pos):
        if self._limited_to_speaker:
            if not self._seek_to_speaker_lock.acquire(blocking = False):
                return

            i = self._segment_index_at_frame(self._current_frame())
            seg = self.merged_dia.segment_at(i)
            if seg.speaker != self._limited_to_speaker:
                self.player.pause()
                i += 1
                while self.merged_dia.segment_at(i).speaker != self._limited_to_speaker:
                    i += 1
                    if i >= self.merged_dia.num_segments:
                        self._limit_to_speaker(None)
                        self._seek_to_speaker_lock.release()
                        return

                self._seek_to_frame(self.merged_dia.segment_at(i).start + 2)
                self.player.play()

            self._seek_to_speaker_lock.release()


    def _on_click(self, event):
        self._seek_to_frame(event.xdata)

    def _on_keypress(self, event):
        if event.key is None:
            return

        if event.key == '?':
            print("")
            print("?           this help message")
            print("space       play/pause")
            print("left/right  10s backward/forward")
            print("p/n         previous/next segment")
            print("m           next unmoderated segment")
            print("l           limit playback to current speaker")
            print("s           save diarization")
            print("u           undo last change")
            print("home        go to beginning")
            print("0-9         change speaker of current segment")
            print("")

        elif event.key == ' ':
            self.player.toggle_pause()

        elif event.key == 'left':
            self.player.seek_relative(-10000)
        elif event.key == 'right':
            self.player.seek_relative(+10000)

        elif event.key in ('p', 'n', 'm'):
            i = self._segment_index_at_frame(self._current_frame())
            if event.key == 'm':
                i += 1
                while self.merged_dia.segment_at(i).speaker.startswith("M"):
                    i += 1
                    if i >= self.merged_dia.num_segments:
                        print("No more unmoderated segments")
                        return
            else:
                i += -1 if event.key == 'p' else 1
                i = max(0, min(self.merged_dia.num_segments - 1, i))
            self._seek_to_frame(self.merged_dia.segment_at(i).start)

        elif event.key == 'l':
            if self._limited_to_speaker is None:
                i = self._segment_index_at_frame(self._current_frame())
                seg = self.merged_dia.segment_at(i)
                self._limit_to_speaker(seg.speaker)
            else:
                self._limit_to_speaker(None)

        elif event.key == 's':
            self.save_to_pickle()

        elif event.key == 'home':
            self._seek_to_frame(0)

        elif event.key == 'u':
            self._undo_update()

        elif event.key.isdigit():
            i = self._segment_index_at_frame(self._current_frame())
            new_dia = self.diarization \
                          .change_speaker(self.merged_dia.segment_at(i).speaker,
                                          "M{}".format(event.key))
            self._undoable_update_diarization(new_dia)

        else:
            print("'{}' isn't bound".format(event.key))


    def _update_diarization(self, new_dia):
        self.diarization = new_dia
        self.merged_dia = new_dia.merge_equal_neighbors()
        self.close()
        self.run()

    def _undoable_update_diarization(self, new_dia):
        self._update_history.append(self.diarization)
        self._update_diarization(new_dia)

    def _undo_update(self):
        self._update_diarization(self._update_history.pop())


    def save_to_pickle(self):
        if self.save_path:
            filename = "dia_{:0>3}_{}.pkl".format(
                self.diarization.num_speakers,
                datetime.now().isoformat()
            )
            path = os.path.join(self.save_path, filename)
            self.diarization.save(path)
            print("Saved history version to {}".format(path))

        if self.save_latest_path:
            self.diarization.save(self.save_latest_path)
            print("Saved latest version to {}".format(self.save_latest_path))
