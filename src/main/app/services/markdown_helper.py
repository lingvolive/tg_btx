

class MarkdownHelper():

    def __init__(self):
        pass

    @staticmethod
    def escape_markdown_symbols(text):
        markdown_symbols = r'\*_`~'
        escaped_text = ''.join(f'\\{char}' if char in markdown_symbols else char for char in text)
        return escaped_text

