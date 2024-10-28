import itertools

spinner = itertools.cycle(["-", "\\", "|", "/"])


def print_progress(processed, total):
    spinner_symbol = next(spinner)
    print(f"{spinner_symbol} {processed}/{total}", end="\r")
