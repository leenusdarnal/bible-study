# Synthetic USFM parser fixtures

These fixtures contain invented sample wording. They are designed to exercise parser behaviour and are not excerpts from a published Bible translation.

Use them to test a USFM 3.0-aware parser. They do not replace validation against the actual WEBP and KJV source archives.

## Files

- 01-basic-book.usfm — book metadata, chapter, heading, paragraph and consecutive verses.
- 02-alternate-numbering.usfm — alternate chapter and verse numbering.
- 03-structured-markup.usfm — poetry, footnote, cross-reference and inline character markers.

## Required parser assertions

1. Preserve source order and source offsets for every marker and text node.
2. Do not treat each physical line as a verse.
3. Preserve primary and alternate numbering independently.
4. Preserve nested footnote/cross-reference structure and inline character markup.
5. Emit no fatal errors for these valid minimal fixtures.
6. Produce deterministic output for repeated runs with the same parser build/configuration.

The fixtures are intentionally small. Add real-source fixtures only after confirming the relevant source archive rights and recording its edition, file path and checksum.
