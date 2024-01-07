import re


def format_text(input_text):
    # Format text between *...*
    input_text = re.sub(r'\*(.*?)\*', r'\033[1m\1\033[0m', input_text)

    # Format text between _..._
    input_text = re.sub(r'_(.*?)_', r'\033[3m\1\033[0m', input_text)

    return input_text

