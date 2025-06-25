import argparse
import string
import random
import json
import os
import logging
from time import time
from pathlib import Path
from collections import defaultdict
from typing import Generator

Automaton = dict[str, tuple[list[str]], list[float]]

LOGGER = logging.getLogger()


def next_character(filename: Path, ignore_case: bool) -> Generator[str, None, None]:
    """Read a file, filter out some characters and yield the other ones

    Parameters
    ----------
    filename : Path
        file to read
    ignore_case : bool
        yield characters in both lower and upper cases

    Yields
    ------
    Generator[str, None, None]
        yield characters, send and return nothing
    """
    non_printable = string.printable[string.printable.index(" ") + 1 :]
    first_char = None
    last_char = None
    with open(filename, "r", encoding="UTF-8") as file:
        for char in file.read():
            if char not in non_printable:
                if not ignore_case:
                    char = char.lower()
                if first_char is None:
                    first_char = char
                yield char
                last_char = char
                
            elif char == "\n" and char != last_char:
                if first_char is None:
                    first_char = char
                yield " "
                last_char = "\n"
    yield first_char

def create_automaton(
    order: int, filename: Path, ignore_case: bool
) -> dict[str, dict[str, int]]:
    """Read a file and create an automaton. For each encountered group of
    characters of length `order`, count the occurrencies of the characters
    following this group

    Parameters
    ----------
    order : int
        lenght of the generating group
    filename : Path
        file to read to get characters
    ignore_case : bool
        set to `False` to only get lower case characters

    Returns
    -------
    dict[str, dict[str, int]]
        Dictionary that associates for each group the number of time each
        character appeared after
    """
    start_time = time()
    automaton = defaultdict(lambda: defaultdict(int))
    gen = next_character(filename, ignore_case)
    curr = ""
    for _ in range(order):
        curr += next(gen)

    for char in gen:
        automaton[curr][char] += 1
        curr = curr[1:] + char
    LOGGER.info(f"Time to generate automaton : {time() - start_time}")
    return normalize_automaton(automaton)


def normalize_automaton(automaton: dict[str, dict[str, int]]) -> Automaton:
    """Given a dictionary that associate each group of characters to the
    following ones and their occurencies, normalize it by changing occurencies
    to frequencies.

    Parameters
    ----------
    automaton : dict[str, dict[str, int]]
        assocaites each group of characters to a dictionary of characters and
        their occurencies

    Returns
    -------
    Automaton
        associates each group of characters to a list of each following
        character, and their frequencies
    """
    start_time = time()
    res = {}
    for state, transitions in automaton.items():
        total_occ = sum(transitions.values())
        res[state] = (
            list(transitions.keys()),
            [v / total_occ for v in transitions.values()],
        )
    LOGGER.info(f"Time to normalize automaton : {time() - start_time}")
    return res


def save_automaton(automaton: Automaton, filename: Path) -> None:
    """Save in a JSON file `automaton`. If needed, creates the 'json' folder to
    store created automatons files. Created file wears the name of the given
    source file

    Parameters
    ----------
    automaton : Automaton
        automaton to save
    filename : Path
        source file of the automaton
    """
    start_time = time()
    if not Path("json").exists():
        os.mkdir("json")
    with open(f"json/{filename.stem}.json", "w", encoding="UTF-8") as file:
        file.write(json.dumps(automaton, indent=4, ensure_ascii=False))
    LOGGER.info(f"Time to save automaton : {time() - start_time}")


def import_automaton(filename: Path) -> Automaton:
    """Read a JSON file at `filename`, and create an automaton

    Parameters
    ----------
    filename : Path

    Returns
    -------
    Automaton
        associates each group of characters to a list of each following
        character, and their frequencies
    """
    start_time = time()
    with open(filename, "r", encoding="UTF-8") as file:
        automaton = json.loads(file.read())
    LOGGER.info(f"Time to import automaton : {time() - start_time}")
    return automaton


def generate(
    length: int,
    order: int,
    filename: Path,
    seed: int | None,
    export: bool,
    raw: bool,
    ignore_case: bool,
    **_,
) -> str:
    """Generate a non-sense but readable string of length `length`, base on
    `filename` file.

    Parameters
    ----------
    length : int
        wanted string length
    order : int
        order of the Markov Chain
    filename : Path
        file to create the automaton from
    seed : int | None
        seed to manage random choices. If not present, default seed will be used
    export : bool
        save automaton into a JSON file
    raw : bool
        set to `False` to indicate that source file is a JSON file
    ignore_case : bool
        set to `True` to get upper case or lower case characters
    Returns
    -------
    str
        Randomly generated string
    """
    start_time = time()
    random.seed(seed)
    if raw:
        automaton = create_automaton(order, filename, ignore_case)
        if export:
            save_automaton(automaton, filename)
    else:
        automaton = import_automaton(filename)

    state = next(iter(automaton))
    res = [None] * length
    index = 0
    gen_start_time = time()
    while index < length:
        res[index] = random.choices(*automaton[state])[0]
        state = state[1:] + res[index]
        index += 1
    LOGGER.info(f"Time generate string : {time() - gen_start_time}")
    LOGGER.info(f"Total time : {time() - start_time}")
    return "".join(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate non-sense but readable\
        text based on an other text, or from an already constructed automaton"
    )
    parser.add_argument(
        "--length", "-l", type=int, default=120, help="Length of text to generate"
    )
    parser.add_argument(
        "--order", "-o", type=int, default=3, help="Order of the Markov Chains"
    )
    parser.add_argument(
        "filename",
        type=Path,
        help="Source of text generation,\
        either a text in an ASCII or UTF-8 format, or a automaton in a json file",
    )
    parser.add_argument(
        "--seed", "-s", type=int, help="Seed for random generation"
    )
    parser.add_argument(
        "--raw",
        "-r",
        action="store_false",
        default=True,
        help="Filename is a text or an already created automaton",
    )
    parser.add_argument(
        "-json",
        action="store_true",
        dest="export",
        help="Extract automaton to json file",
    )
    parser.add_argument(
        "--ignore-case",
        "-c",
        action="store_true",
        dest="ignore_case",
        help="Ignore case",
    )
    parser.add_argument(
        "--log", "-L", type=Path, help="Placement to write logs"
    )
    args = vars(parser.parse_args())
    if args["log"]:
        logging.basicConfig(filename=args["log"], level=logging.INFO)
    print(generate(**args))
