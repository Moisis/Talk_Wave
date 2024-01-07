from colorama import Fore, Style, init

# Initialize colorama to work on Windows as well
init()

class MessageFormatter:
    @classmethod
    def format(cls, text):
        formatted_text = text

        # Bold formatting (*text*)
        start_bold = formatted_text.find('*')
        end_bold = formatted_text.find('*', start_bold + 1)
        if start_bold != -1 and end_bold != -1:
            bold_text = formatted_text[start_bold + 1:end_bold]
            formatted_text = formatted_text.replace(f'*{bold_text}*', f'{Style.BRIGHT}{bold_text}{Style.RESET_ALL}')

        # Italic formatting (_text_)
        start_italic = formatted_text.find('_')
        end_italic = formatted_text.find('_', start_italic + 1)
        if start_italic != -1 and end_italic != -1:
            italic_text = formatted_text[start_italic + 1:end_italic]
            formatted_text = formatted_text.replace(f'_{italic_text}_', f'{Style.BRIGHT}{Fore.BLACK}{italic_text}{Style.RESET_ALL}')

        return formatted_text


# User input
user_message = input("Enter your message: ")

# Format the message based on user input
formatted_message = MessageFormatter.format(user_message)
print(formatted_message)
