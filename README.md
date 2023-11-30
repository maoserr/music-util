# Musician Utilities

A collection of tools for musicians.


## Vocal remover

Splits MP3 file into vocal and background, using demucs as default.

You can also split out guitar, bass, drums, etc if you remove the two-stem argument.

[Demucs](https://github.com/facebookresearch/demucs)

![Voc](doc/voc_remover.png?raw=true "Vocals")

## Transcription

Attempts to generate note graph using MP3 file. 
This only works if there's one note per time, and not on chords.

[Crepe](https://github.com/marl/crepe)

![Tra](doc/trans.png?raw=true "Transcription")
