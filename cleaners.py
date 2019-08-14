'''
Cleaners are transformations that run over the input eng_text_norm at both training and eval time.

Cleaners can be selected by passing a comma-delimited list of cleaner names as the "cleaners"
hyperparameter. Some cleaners are English-specific. You'll typically want to use:
  1. "english_cleaners" for English eng_text_norm
  2. "transliteration_cleaners" for non-English eng_text_norm that can be transliterated to ASCII using
     the Unidecode library (https://pypi.python.org/pypi/Unidecode)
  3. "basic_cleaners" if you do not want to transliterate (in this case, you should also update
     the symbols in symbols.py to match your data).
'''

import re
from unidecode import unidecode
from .numbers import normalize_numbers


# Regular expression matching whitespace:
_whitespace_re = re.compile(r'\s+')


# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [(re.compile('\\b%s\\.' % x[0], re.IGNORECASE), x[1]) for x in [
    ('mrs', 'misess'),
    ('mr', 'mister'),
    ('dr', 'doctor'),
    ('st', 'saint'),
    ('co', 'company'),
    ('jr', 'junior'),
    ('maj', 'major'),
    ('gen', 'general'),
    ('drs', 'doctors'),
    ('rev', 'reverend'),
    ('lt', 'lieutenant'),
    ('hon', 'honorable'),
    ('sgt', 'sergeant'),
    ('capt', 'captain'),
    ('esq', 'esquire'),
    ('ltd', 'limited'),
    ('col', 'colonel'),
    ('ft', 'fort'),
]]


def expand_abbreviations(text):
    for regex, replacement in _abbreviations:
        text = re.sub(regex, replacement, text)
    return text


# List of english symbolic expressions:
_symbolic_expressions = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('\\\\~/', ''),
    ('\^5', ''),
    ('\?\^', ''),
    ('\\\\_/\?', ''),
    ('\[_\]>', ''),
    ('@@@', ''),
    ('@--/--', ''),
    (':\)', ''),
    ('0:-\)', ''),
    ('!:-\)', ''),
    (':-\)', ''),
    (';-\)~', ''),
    (';-\)', ''),
    ('<:-\|', ''),
    (':~\)', ''),
    ('>:-\(', ''),
    (':-\(', ''),
    ('#8-\)', ''),
    ('8-\)', ''),
    (':-}', ''),
    (':-/', ''),
    (':,-\(', ''),
    (':-<', ''),
    ('>:-\|\|', ''),
    (':-\|', ''),
    (':->', ''),
    ('\|-\)', ''),
    ('=:-0', ''),
    (':-0', ''),
    (':-o', ''),
    (':-D', ''),
    (':-x', ''),
    (':o\)', ''),
    (';-P', ''),
    (':P', ''),
    ('&-\(', ''),
    (';-{\)', ''),
    (';~\)', ''),
    ('c\["\]', ''),
    ('<:-|', ''),
    ('\|-\|', ''),
]]


def remove_symbolic_expressions(text):
    for regex, replacement in _symbolic_expressions:
        text = re.sub(regex, replacement, text)
    return text


# List of english symbolic acronym:
_symbolic_acronym = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('can\'t', 'can not'),
    ('cannot', 'can not'),
    ('what\'s', 'what is'),
    ('\'ve ', ' have '),
    ('n\'t ', ' not '),
    ('i\'m', 'i am'),
    ('\'re ', ' are '),
    ('he\'s ', ' he is '),
    ('she\'s ', ' she is '),
    ('it\'s ', ' it is '),
    ('that\'s ', ' that is '),
    ('\'d ', ' would '),
    ('\'ll ', ' will '),
]]


def expand_acronym(text):
    for regex, replacement in _symbolic_acronym:
        text = re.sub(regex, replacement, text)
    return text


# Remove ordinal:
_ordinal_re = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('\(?\d+\)', ''),
    ('\[\d+\]', ''),
    ('\<\d+\>', ''),
    ('\{\d+\}', ''),
]]


def remove_ordinal(text):
    for regex, replacement in _ordinal_re:
        text = re.sub(regex, replacement, text)
    return text


# Process english punctuations:
_punctuations = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('，', ','),
    ('；', ';'),
    ('。', '.'),
    ('！', '!'),
    ('？', '?'),
    ('[()]', ' '),
    ('\s*[.]+', '.$'),
    ('\s*[!]+', '!$'),
    ('\s*[?]+', '?$'),
    ('\s*[-]+', '.$'),
    ('\s*,', ', '),
    ('\s*;', ' ; '),
    ('\"', ''),
]]


def normalize_punctuations(text):
    for regex, replacement in _punctuations:
        text = re.sub(regex, replacement, text)
    return text


# Symbols replacement:
_symbols = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('&', ' and '),
    ('\|', ' or '),
    ('#', ' number '),
    ('\*', ''),
]]


_time_operator_re = re.compile(r'(\d+\w?)\s*(x|\*)\s*')


def normalize_operator(text):
    text = re.sub(_time_operator_re, lambda m: ' '+m.group(1)+' times ', text)
    return text


def replace_symbols(text):
    for regex, replacement in _symbols:
        text = re.sub(regex, replacement, text)
    return text


def expand_numbers(text):
    return normalize_numbers(text)


def lowercase(text):
    return text.lower()


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


def convert_to_ascii(text):
    return unidecode(text)


def basic_cleaners(text):
    '''Basic pipeline that lowercases and collapses whitespace without transliteration.'''
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def transliteration_cleaners(text):
    '''Pipeline for non-English eng_text_norm that transliterates to ASCII.'''
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = collapse_whitespace(text)
    return text


def english_cleaners(text):
    '''Pipeline for English eng_text_norm, including number and abbreviation expansion.'''
    text = convert_to_ascii(text)
    text = remove_symbolic_expressions(text)
    text = lowercase(text)
    text = expand_acronym(text)
    text = remove_ordinal(text)
    # eng_text_norm = expand_numbers(eng_text_norm)
    text = expand_abbreviations(text)
    text = normalize_punctuations(text)
    text = normalize_operator(text)
    text = replace_symbols(text)
    text = collapse_whitespace(text)
    return text
