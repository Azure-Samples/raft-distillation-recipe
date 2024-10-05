# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List, cast

import nltk
import numpy as np

try:
    from nltk.tokenize.nist import NISTTokenizer
except LookupError:
    nltk.download("perluniprops")
    nltk.download("punkt")
    nltk.download("punkt_tab")
    from nltk.tokenize.nist import NISTTokenizer


def nltk_tokenize(text: str) -> List[str]:
    """Tokenize the input text using the NLTK tokenizer."""

    is_latin_or_numeric = all(
        ("\u0020" <= c <= "\u007E")  # Basic Latin
        or ("\u00A0" <= c <= "\u00FF")  # Latin-1 Supplement
        or ("0" <= c <= "9")  # Digits
        for c in text
    )

    if is_latin_or_numeric:
        return cast(List[str], nltk.word_tokenize(text))

    return list(NISTTokenizer().international_tokenize(text))