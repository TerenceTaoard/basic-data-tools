# Texstats Examples

An example input text is found in sample.txt.

## Example commands

A basic command: (expected output in expected.txt)

```bash
python scripts/textstats.py --input examples/textstats/sample.txt
```

List the top 10 words: (expected output in expected_top_words.txt)

```bash
python scripts/textstats.py --input examples/textstats/sample.txt --top-words 10
```

Convert all letters to lowercase first and format as JSON: (expected output in expected_lowercase.json)

```bash
python scripts/textstats.py --input examples/textstats/sample.txt --format json --lowercase
```