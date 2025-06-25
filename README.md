# markov-chain

Generate non-sense but readable text based on an other text, or from an already constructed automaton

## Examples
Examples of different order, from Oliver Twist by Charles Dickens :

- order is 1 : `l toruthen das.'h alye, nd cct doy he withtthe s t uned wackny sit? s, ff ided jecy. il f d o  bapoco rive ved there ino`
- order is 2 : `e lood orntin thaps fithe earrace,' the sin haturse. int mat mor yoused laterren, a possaid-hatch a him yought, beeigir?`
- order is 3 : `v old _shaking it is-she warley eyes, and pour to retition tooking head, tumble, and litingly: into the ma'am?' 'say dis`
- order is 4 : `er, the very britted probable.  you canding in impatiently difficers, love up. it company prison his a poor fond on his `
- order is 5 : `r's, raised to departments, in a sick chamber, and curling oliver had not have space arose, sunk in advantageous word. w`

# Arguments

```
positional arguments:
  filename              Source of text generation, either a text in an ASCII or UTF-8 format, or a automaton in a json file

options:
  -h, --help            show this help message and exit
  --length LENGTH, -l LENGTH
                        Length of text to generate
  --order ORDER, -o ORDER
                        Order of the Markov Chains
  --seed SEED, -s SEED  Seed for random generation
  --raw, -r             Filename is a text or an already created automaton
  -json                 Extract automaton to json file
  --ignore-case, -c     Ignore case
  --log LOG, -L LOG     Placement to write logs
```

# JSON Automaton

Example on the word "mississippi", with an order of 1

```json
{
    "m": [
        ["i"],
        [1.0]
    ],
    "i": [
        ["s", "p", "m"],
        [0.5, 0.25, 0.25]
    ],
    "s": [
        ["s", "i"],
        [0.5, 0.5]
    ],
    "p": [
        ["p", "i"],
        [0.5, 0.5]
    ]
}
```

