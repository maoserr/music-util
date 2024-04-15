# Musician Utilities

A collection of tools for musicians.


## Vocal remover

Splits MP3 file into vocal and background, using demucs as default.

You can also split out guitar, bass, drums, etc if you remove the two-stem argument.

[Demucs](https://github.com/facebookresearch/demucs)

![Voc](https://raw.githubusercontent.com/maoserr/music-util/develop/doc/voc_remover.png?raw=true "Vocals")

## Transcription

Attempts to generate sheet music using MP3 file.
This only works if there's one note per time, and not on chords.
(Mostly as a starting point for manual transcription, and not an accurate solution.)

MP3 is converted into a Lilypond file (.ly). You can then compile into PDFs.

[Crepe](https://github.com/marl/crepe)

![Tra](https://raw.githubusercontent.com/maoserr/music-util/develop/doc/trans.png?raw=true "Transcription")

Sample Lilypond results:
```
{
r1 r1 ais2 cis'1 cis'1 f'8 gis'8 
 r4 gis'1 fis'2 dis'1 r2 ais8 cis'4 
 ais8 cis'4 r16 dis'2 fis'1 r16 ais4 
 b16 r1 gis2 r1 cis'1 dis'4 f'2 
 gis'1 gis'1 dis'2 r1 f'4 r1 r1 
 cis'1 cis'1 r8 ais16 a2 r4 cis'4 
 ...
}
```
