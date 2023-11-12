import nltk
from nltk.corpus import cmudict
import re

# Initialize the CMU Pronouncing Dictionary
d = cmudict.dict()

def count_syllables(word):
    word = word.lower()
    if word not in d:
        # Word not in dictionary, use rule-based method as a fallback
        return count_syllables_rule_based(word)
    return max([len(list(y for y in x if y[-1].isdigit())) for x in d[word]])


def count_syllables_rule_based(word):
    word = word.lower()
    syllable_count = 0
    
    # Remove trailing 'e' to avoid over-counting
    if word.endswith('e'):
        word = word[:-1]
        
    # Split the word into vowel sequences
    vowels = 'aeiouy'
    vowel_sequences = re.findall(f'[{vowels}]+', word)
    
    # Count vowel sequences as syllables
    syllable_count = len(vowel_sequences)
    
    # Special cases where 'y' at the start isn't a vowel sound
    if word.startswith('y'):
        syllable_count -= 1
    
    # Return at least 1 syllable for any word
    return max(syllable_count, 1)

# Example usage:
print(count_syllables('I have been one acquainted'))  # Output should be 2
print(count_syllables('syllable'))  # Output should be 3

def get_stress_pattern(word):
    word = word.lower()
    if word not in d:
        return None  # Word not in dictionary
    # Taking the first pronunciation variant
    stresses = [char for phone in d[word][0] for char in phone if char.isdigit()]
    return ''.join(['/' if s == '1' else 'u' for s in stresses])

def analyze_line(line):
    words = nltk.word_tokenize(line)
    stress_pattern = []
    for word in words:
        stress = get_stress_pattern(word)
        if stress:
            stress_pattern.append(stress)
    return ' '.join(stress_pattern)

# Example usage
line = "I have been one acquainted with the night"
print(analyze_line(line))

