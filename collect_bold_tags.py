import os
import re

# Define the path where your .md files are located
directory_path = "/Users/viktorkertanov/Library/Mobile Documents/iCloud~md~obsidian/Documents/emails_for_poems"
output_path = "/Users/viktorkertanov/Library/Mobile Documents/iCloud~md~obsidian/Documents/"

# Regular expression patterns
pattern_bold = r'\*\*([^\*]+)\*\*'
pattern_hashtag = r'#(en|ru)\b'

# Dictionaries to store extracted bolded text by language
collected_bolded_text = {
    'en': [],
    'ru': [],
    'default': []
}

# Loop over all files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.md'):
        with open(os.path.join(directory_path, filename), 'r', encoding='utf-8') as file:
            content = file.read()
            bolded_text = re.findall(pattern_bold, content)
            hashtags = re.findall(pattern_hashtag, content)
            language = 'default' if not hashtags else hashtags[0]

            collected_bolded_text[language].extend(bolded_text)

# Save the extracted bold text to files
for language, bold_texts in collected_bolded_text.items():
    output_filename = os.path.join(output_path, f'bold_collected_{language}.md')

    # Read the existing content of the output file
    existing_content = ""
    if os.path.exists(output_filename):
        with open(output_filename, 'r', encoding='utf-8') as output_file:
            existing_content = output_file.read()

    # Append non-duplicate bolded text to the output file
    with open(output_filename, 'a', encoding='utf-8') as output_file:
        for idx, text in enumerate(bold_texts, start=1):
            if len(text)<=1:
                continue
            bolded_text_md = f"{idx}. {text}\n"
            if bolded_text_md not in existing_content:
                output_file.write(bolded_text_md)

    print(f"Collected bold text ({language}) written to: {output_filename}")
