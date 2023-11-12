import spacy
import os
import re

# Load English tokenizer, POS tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

directory_path = "/Users/viktorkertanov/Library/Mobile Documents/iCloud~md~obsidian/Documents/emails_for_poems"

# Define a set to hold unique noun chunks
chunks_set = set()

for filename in os.listdir(directory_path):
    if filename.endswith('.md'):
        with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
            content = file.read()
            doc = nlp(content)
            for chunk in doc.noun_chunks:
                # Clean up each chunk by removing line breaks and extra spaces
                clean_chunk = re.sub(r'\s+', ' ', chunk.text).strip()
                chunks_set.add(clean_chunk)

# Convert the set into a sorted list
chunks_list = sorted(list(chunks_set))

# Print the results
for i, chunk in enumerate(chunks_list, 1):
    print(f"{i}. {chunk}")
