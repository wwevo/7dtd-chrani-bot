def is_alpha(word):
    try:
        return word.encode('ascii').isalpha()
    except Exception:
        return False
