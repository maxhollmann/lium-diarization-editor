A very simple viewer/editor for LIUM speaker diarizations.

# Installation

    pip install lium-diarization-editor


# Usage

The package provides the command `lium-dia-edit`:

    Usage: lium-dia-edit [OPTIONS]

      View or edit a diarization.

    Options:
      -a, --audio TEXT        Load an audio file belonging to the diarization.
      -d, --dia TEXT          A LIUM diarization file.
      -p, --pickled-dia TEXT  A pickled diarization, as created using the --save
                              option.
      -s, --save TEXT         Where to save the diarization (as pickle) when
                              pressing "s".
      --help                  Show this message and exit.


Within the editor, use the following keys to do stuff:

| Key        | Function                                    |
|------------|---------------------------------------------|
| space      | play/pause                                  |
| left/right | 10s backward/forward                        |
| p/n        | previous/next segment                       |
| m          | next unmoderated segment                    |
| l          | limit playback to current speaker           |
| s          | save diarization                            |
| u          | undo last change                            |
| home       | go to beginning                             |
| 0-9        | change speaker of current segment to M<0-9> |


# Contributing

* Install [pipenv](https://pipenv.readthedocs.io/en/latest/)
* Fork and clone the [repository](https://github.com/maxhollmann/lium-diarization-editor)
* In the repository, run `pipenv install --dev` to install required packages and the package itself into a virtualenv
* To activate the virtualenv, run `pipenv shell`
* Make changes, commit, push
* Create a pull request
