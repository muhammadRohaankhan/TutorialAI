def fix_misencoded_text(text):
    if isinstance(text, str):
        bytes_text = text.encode('latin1', errors='ignore')
        return bytes_text.decode('utf-8', errors='ignore')
    else:
        return text

def decode_and_fix_text(s):
    if isinstance(s, str):
        s_fixed = fix_misencoded_text(s)
        return s_fixed.encode('utf-8').decode('unicode_escape')
    else:
        return s
