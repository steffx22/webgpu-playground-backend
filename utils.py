from better_profanity import profanity

profanity.load_censor_words_from_file("SwearFilter.txt")

def profanity_check(word: str) -> bool:
    delimiters = "/?.>,<'@;:]}[{=+-_)(*&^%$£"
    for char in delimiters:
        word = word.replace(char, " ")
    return profanity.censor(word) != word