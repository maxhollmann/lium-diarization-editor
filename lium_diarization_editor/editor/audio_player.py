from mpv import MPV

class AudioPlayer:
    def __init__(self, filename):
        self.filename = filename

        self.mpv = MPV(input_default_bindings = True,
                       input_vo_keyboard = True)
        self.mpv.pause = True
        self.mpv.play(self.filename)

        self.mpv.wait_for_property("length")
        self.length = self.mpv.length * 1000


    def position(self):
        return self.mpv.time_pos * 1000

    def progress(self):
        return self.position() / self.length


    def pause(self):
        self.mpv.pause = True
    def play(self):
        self.mpv.pause = False
    def toggle_pause(self):
        self.mpv.pause = not self.mpv.pause

    def seek_progress(self, progress):
        self.mpv.seek(self.mpv.length * progress, "absolute", "exact")

    def seek_relative(self, ms):
        self.mpv.time_pos += ms / 1000


    def observe_position(self, observer):
        def converting_observer(prop, value):
            observer(value * 1000)
        self.mpv.observe_property("time-pos", converting_observer)


    def __del__(self):
        # TODO may never be called, see https://github.com/RafeKettler/magicmethods/blob/master/magicmethods.pdf
        self.mpv.quit()
        self.mpv.terminate()
