import sys

def progressbar(current, total):
    bar_length = 60
    filled_length = int(bar_length*current/total)

    percent = round(current/total*100,1)

    bar = (filled_length * "=") + (bar_length-filled_length) * "-"
    progressbar_str = f'[{bar}] {percent}%'
    sys.stdout.write(f'Extracting.. {progressbar_str}\r')
    sys.stdout.flush()