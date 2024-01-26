

class tgUtils():

    def __init__(self):
        pass

    @staticmethod
    def remove_markdown_symbols(text):
        markdown_symbols = ["*", "_", "[", "]", "(", ")", "`", ">", "#", "+", "-"]
        cleaned_text = "".join([char for char in text if char not in markdown_symbols])
        return cleaned_text