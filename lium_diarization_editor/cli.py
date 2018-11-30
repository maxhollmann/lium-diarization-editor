import click

from lium_diarization_editor import Diarization
from lium_diarization_editor.lium import load_diarization as load_lium_diarization
from lium_diarization_editor.editor import DiarizationEditor
from lium_diarization_editor.editor import AudioPlayer


@click.group()
def cli():
    pass



@click.command(help='View or edit a diarization.')
@click.option(
    '--audio', '-a', 'audio_file',
    help='Load an audio file belonging to the diarization.')
@click.option(
    '--dia', '-d', 'dia_file',
    help='A LIUM diarization file.')
@click.option(
    '--pickled-dia', '-p', 'pickled_dia_file',
    help='A pickled diarization, as created using the --save option.')
@click.option(
    '--save', '-s', 'save_path',
    help='Where to save the diarization (as pickle) when pressing "s".')

def main(dia_file=None, pickled_dia_file=None, audio_file=None, save_path=None):
    if audio_file:
        player = AudioPlayer(audio_file)
    else:
        player = None

    if dia_file:
        diarization = load_lium_diarization(dia_file)
    else:
        if pickled_dia_file is None:
            print("One of --dia and --pickled-dia is required. "
                  "Run with --help to see all options.")
            exit(1)
        diarization = Diarization.load(pickled_dia_file)

    editor = DiarizationEditor(diarization, player, save_latest_path=save_path)
    editor.run()


if __name__ == '__main__':
    main()
