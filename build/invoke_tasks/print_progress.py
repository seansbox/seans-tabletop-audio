import itertools
import shutil

spinner = itertools.cycle(["-", "\\", "|", "/"])

# Determine terminal width once and set MESSAGE_WIDTH accordingly
TERMINAL_WIDTH = shutil.get_terminal_size((80, 20)).columns
MESSAGE_WIDTH = max(0, TERMINAL_WIDTH - 15)  # Leave space for spinner and counts


def print_progress(message, processed=0, total=0, show_every=1, message_width=MESSAGE_WIDTH):
    """
    Print progress with a spinner symbol, showing the status every `show_every` steps.
    If `processed` and `total` are not specified, only the message will be printed.
    If `processed` equals `total`, a '-' symbol is displayed instead of the spinner.

    Args:
        message (str): Message to display after the progress count.
        processed (int): The number of items processed so far (default is 0).
        total (int): The total number of items to process (default is 0).
        show_every (int): The interval of steps at which to print the progress.
        message_width (int): Fixed width for the message to maintain consistent display.
                             Defaults to the calculated MESSAGE_WIDTH based on terminal size.
    """
    if processed > 0 and total > 0:
        if len(message) > message_width:
            display_message = message[: message_width - 3] + "..."  # Truncate and add ellipsis
        else:
            display_message = message.ljust(message_width)  # Pad with spaces

        if processed % show_every == 0 or processed == total:
            symbol = "-" if processed == total else next(spinner)
            print(f"{symbol} {processed}/{total} {display_message}", end="\r")

        if processed == total:
            print()  # Move to the next line at the end of progress
    else:
        print(f"- {message}")
