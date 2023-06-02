FILTER_BY_NAME_BY_CATEGORY_BY_SCRIPT = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 2,
    "results": [
        {"character": "⳰", "name": "COPTIC COMBINING SPIRITUS ASPER", "codepoint": "U+2CF0", "uriEncoded": "%E2%B3%B0"},
        {"character": "⳱", "name": "COPTIC COMBINING SPIRITUS LENIS", "codepoint": "U+2CF1", "uriEncoded": "%E2%B3%B1"},
    ],
}

INVALID_PAGE_NUMBER = {"detail": "Request for page #2 is invalid since there is only 1 total page."}

NO_CHARS_MATCH_SETTINGS = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 0,
    "totalResults": 0,
    "results": [],
}

FILTER_BY_UNICODE_AGE = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 4,
    "results": [
        {"character": "࢈", "name": "ARABIC RAISED ROUND DOT", "codepoint": "U+0888", "uriEncoded": "%E0%A2%88"},
        {"character": "꭪", "name": "MODIFIER LETTER LEFT TACK", "codepoint": "U+AB6A", "uriEncoded": "%EA%AD%AA"},
        {"character": "꭫", "name": "MODIFIER LETTER RIGHT TACK", "codepoint": "U+AB6B", "uriEncoded": "%EA%AD%AB"},
        {"character": "﯂", "name": "ARABIC SYMBOL WASLA ABOVE", "codepoint": "U+FBC2", "uriEncoded": "%EF%AF%82"},
    ],
}

FILTER_BY_BIDIRECTIONAL_CLASS = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 1,
    "results": [{"character": "₫", "name": "DONG SIGN", "codepoint": "U+20AB", "uriEncoded": "%E2%82%AB"}],
}

FILTER_BY_DECOMPOSITION_TYPE = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 6,
    "results": [
        {"character": "⑦", "name": "CIRCLED DIGIT SEVEN", "codepoint": "U+2466", "uriEncoded": "%E2%91%A6"},
        {"character": "⑰", "name": "CIRCLED NUMBER SEVENTEEN", "codepoint": "U+2470", "uriEncoded": "%E2%91%B0"},
        {"character": "㉗", "name": "CIRCLED NUMBER TWENTY SEVEN", "codepoint": "U+3257", "uriEncoded": "%E3%89%97"},
        {"character": "㊆", "name": "CIRCLED IDEOGRAPH SEVEN", "codepoint": "U+3286", "uriEncoded": "%E3%8A%86"},
        {"character": "㊲", "name": "CIRCLED NUMBER THIRTY SEVEN", "codepoint": "U+32B2", "uriEncoded": "%E3%8A%B2"},
        {"character": "㊼", "name": "CIRCLED NUMBER FORTY SEVEN", "codepoint": "U+32BC", "uriEncoded": "%E3%8A%BC"},
    ],
}

FILTER_BY_LINE_BREAK_TYPE = {
    "url": "/v1/characters/filter",
    "hasMore": True,
    "currentPage": 1,
    "nextPage": 2,
    "totalResults": 13,
    "results": [
        {"character": ",", "name": "COMMA", "codepoint": "U+002C", "uriEncoded": "%2C"},
        {"character": ".", "name": "FULL STOP", "codepoint": "U+002E", "uriEncoded": "%2E"},
        {"character": ":", "name": "COLON", "codepoint": "U+003A", "uriEncoded": "%3A"},
        {"character": ";", "name": "SEMICOLON", "codepoint": "U+003B", "uriEncoded": "%3B"},
        {"character": ";", "name": "GREEK QUESTION MARK", "codepoint": "U+037E", "uriEncoded": "%CD%BE"},
        {"character": "։", "name": "ARMENIAN FULL STOP", "codepoint": "U+0589", "uriEncoded": "%D6%89"},
        {"character": "،", "name": "ARABIC COMMA", "codepoint": "U+060C", "uriEncoded": "%D8%8C"},
        {"character": "؍", "name": "ARABIC DATE SEPARATOR", "codepoint": "U+060D", "uriEncoded": "%D8%8D"},
        {"character": "߸", "name": "NKO COMMA", "codepoint": "U+07F8", "uriEncoded": "%DF%B8"},
        {"character": "⁄", "name": "FRACTION SLASH", "codepoint": "U+2044", "uriEncoded": "%E2%81%84"},
    ],
}

FILTER_BY_CCC = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 1,
    "results": [{"character": "᷎", "name": "COMBINING OGONEK ABOVE", "codepoint": "U+1DCE", "uriEncoded": "%E1%B7%8E"}],
}

FILTER_BY_NUMERIC_TYPE = {
    "url": "/v1/characters/filter",
    "hasMore": False,
    "currentPage": 1,
    "totalResults": 4,
    "results": [
        {"character": "𐩀", "name": "KHAROSHTHI DIGIT ONE", "codepoint": "U+10A40", "uriEncoded": "%F0%90%A9%80"},
        {"character": "𐩁", "name": "KHAROSHTHI DIGIT TWO", "codepoint": "U+10A41", "uriEncoded": "%F0%90%A9%81"},
        {"character": "𐩂", "name": "KHAROSHTHI DIGIT THREE", "codepoint": "U+10A42", "uriEncoded": "%F0%90%A9%82"},
        {"character": "𐩃", "name": "KHAROSHTHI DIGIT FOUR", "codepoint": "U+10A43", "uriEncoded": "%F0%90%A9%83"},
    ],
}

INVALID_FILTER_PARAM_VALUES = {
    "detail": "Invalid values were provided for the following 9 parameters:\n\n2 values provided for the 'category' parameter are invalid: ['aa', 'bb']\n\n2 values provided for the 'age' parameter are invalid: ['7.1', '12.97']\n\n2 values provided for the 'script' parameter are invalid: ['blar', 'blee']\n\n2 values provided for the 'bidi_class' parameter are invalid: ['vv', 'rr']\n\n1 value provided for the 'decomp_type' parameter is invalid: ['gosh']\n\n1 value provided for the 'line_break' parameter is invalid: ['ha']\n\n1 value provided for the 'combining_class' parameter is invalid: ['300']\n\n1 value provided for the 'num_type' parameter is invalid: ['dd']\n\n2 values provided for the 'show_props' parameter are invalid: ['soup', 'salad']"
}
