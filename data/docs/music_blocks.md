# Music Blocks

## Overview

Music Blocks is a visual programming language and collection of Activities focused on music and art. It is one of Sugar Labs' flagship projects, developed primarily by Walter Bender. Music Blocks allows children to explore music concepts like pitch, rhythm, timbre, and musical intervals through code.

Music Blocks is available both as a Sugar Activity and as a standalone web application at https://musicblocks.sugarlabs.org. The web version runs in any modern browser and does not require Sugar to be installed.

## How Music Blocks Works

Music Blocks uses a block-based programming paradigm similar to Scratch and Turtle Blocks. Children drag and snap together blocks to create musical compositions. The key block categories include:

- **Pitch blocks**: Set the note pitch (C, D, E, F, G, A, B) and octave
- **Rhythm blocks**: Define note duration (whole, half, quarter, eighth notes)
- **Tone blocks**: Control timbre and instrument sounds
- **Flow blocks**: Loops, conditionals, and sequence control
- **Action blocks**: Define reusable procedures (functions)
- **Widget blocks**: Open interactive widgets like the Pitch-Time Matrix

## Programming with Music Blocks

A simple melody in Music Blocks:
1. Start with a "Start" block
2. Add a "Note" block with duration (e.g., quarter note)
3. Inside the Note block, add a "Pitch" block (e.g., C4)
4. Repeat for additional notes

Music Blocks supports polyphony (multiple voices), custom instruments via synthesizer blocks, and export to MIDI and Lilypond formats for sheet music generation.

## Technical Architecture

The web-based Music Blocks is built with:
- JavaScript (vanilla JS, no framework)
- Web Audio API for sound synthesis
- SVG for the visual block interface
- Service Workers for offline support

The Sugar Activity version wraps the web application using WebKit.

## Getting Involved

Music Blocks development happens on GitHub at https://github.com/sugarlabs/musicblocks. The project welcomes contributions in JavaScript, UI/UX design, music education content, and translations. Walter Bender (walterbender) is the lead maintainer.

For the next-generation version (Music Blocks v4), development is at https://github.com/sugarlabs/musicblocks-v4, which uses TypeScript and a modern component architecture.
