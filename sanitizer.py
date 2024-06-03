import re
from unidecode import unidecode 

def sanitize_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)

    # Remove leading and trailing whitespace
    text = text.strip()

    # Remove redundant spaces after newline
    text = re.sub(r"\n[\n\t\s]{1,}","\n",text)

    # Remove "\xa0" 
    text = re.sub(r"\xa0"," ",text)

    # Remove everything that is not ASCII or extended ASCII (except for accented letters)
    whitelist = ["Ç","ü","â","ä","à","α","β","γ","δ","ε","η","θ","λ","μ","π","σ","ω","φ","å","ç","ê","ë","è","ï","î","ì","Ä","Å","É","ô","ö","ò","û","ù","ÿ","Ö","Ü","á","í","ó","ú","ñ","Ñ","°","À","È","Ì","Ò","Ù", "€", "$","£","¥"]
    
    text = re.sub(r'[«,»]','"', text)

    ''.join(ch if ch in whitelist else unidecode(ch) for ch in text)

    return text