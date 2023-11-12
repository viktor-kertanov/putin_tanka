import mailbox
from email.header import decode_header
from email import message_from_string
import os
import re
from datetime import datetime
from langdetect import detect
import spacy
from spacy.lang.ru import Russian
from spacy.lang.en import English
import arrow
from itertools import islice
import numpy as np
import csv
import pyphen

# Load the spaCy models
nlp_en = spacy.load('en_core_web_sm')
nlp_ru = spacy.load('ru_core_news_sm')
dic = pyphen.Pyphen(lang='en')

# Function to generate hashtags using spaCy
def generate_hashtags(text, language):
    hashtags = []

    if language == 'en':
        doc = nlp_en(text)
        # Use noun chunks for English
        hashtags = ['#' + chunk.root.text for chunk in doc.noun_chunks]
    elif language == 'ru':
        doc = nlp_ru(text)
        # Use lemmatized forms of nouns, proper nouns, and adjectives for Russian
        significant_tokens = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
        hashtags = ['#' + token.lower() for token in significant_tokens]

    # Filter out unwanted hashtags and ensure unique hashtags
    hashtags = list({tag for tag in hashtags if len(tag) > 2})[:10]

    return hashtags

def is_html_like_content(text):
    if text is None:
        return False
    html_tags = ['<html', '<body', '<div', '<span', '<a href', '<table', '<td', '<tr', '<img']
    return any(tag in text.lower() for tag in html_tags)

def decode_email_header(header):
    if not header:
        return ""
    
    decoded = decode_header(header)
    header_parts = []

    for decoded_part, encoding in decoded:
        if isinstance(decoded_part, bytes):
            if not encoding:
                header_parts.append(decoded_part.decode('utf-8', errors='replace'))
            else:
                header_parts.append(decoded_part.decode(encoding, errors='replace'))
        else:
            header_parts.append(decoded_part)
    
    return ' '.join(header_parts)

def extract_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            charset = part.get_content_charset()  # Obtain charset from the email part
            if content_type == "text/plain":
                body_bytes = part.get_payload(decode=True)
                try:
                    body = body_bytes.decode(charset if charset else 'utf-8')
                except (UnicodeDecodeError, LookupError):  # Handle both decoding errors and invalid charset names
                    body = body_bytes.decode('utf-8', errors='replace')  # Replace invalid characters
                return remove_urls(clean_markdown(body)).strip()
    else:
        return remove_urls(clean_markdown(msg.get_payload())).strip()

def remove_urls(text):
    url_pattern = re.compile(
        r'https?%3A%2F%2F(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.sub('', text)

def clean_markdown(text):
    cleaned = text.replace('**', '').replace('*', '').replace(' (', '')
    cleaned = re.sub(r'\s*\(\s*', '', cleaned)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    return re.sub(' +', ' ', cleaned)

def format_date(date_str):
    try:
        # Use arrow to parse the date string
        dt = arrow.get(date_str, ["ddd, D MMM YYYY H:m:s Z", "ddd, D MMM YYYY H/m/s Z", "ddd, D MMM YYYY H/M/S Z"])
        # Format the datetime object into the desired string format
        return dt.format("YYYY-MM-DD_HH-MM-SS")
    except (arrow.parser.ParserMatchError, arrow.ParserError) as e:
        # If arrow can't parse the date, use the current datestamp
        return arrow.now().format("YYYY-MM-DD_HH-MM-SS")


def determine_language(message, body):
    content_language = message.get('Content-Language')
    if content_language:
        if 'en' in content_language:
            return 'en'
        elif 'ru' in content_language:
            return 'ru'

    # If Content-Language header is not definitive, use langdetect
    try:
        detected_language = detect(body)
        if detected_language in ['en', 'ru']:
            return detected_language
    except:
        pass

    return None  # if we can't determine the language

def sanitize_filename(filename):
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        filename = filename.replace(char, '_')  # replace invalid chars with underscore
    return filename

# Define a custom function to check if a token is an imperative verb
def is_imperative(doc):
    for sent in doc.sents:
        for token in sent:
            # An imperative verb is a verb that is at the start of a sentence,
            # is in base form, and whose subject (typically "you") is not stated but implied.
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                return True
                # Check if the first token of a sentence is a verb (potential imperative)
                # if sent[0].pos_ == "VERB" and sent[0].lemma_ == token.lemma_:
                #     return True
                # # Also check if the verb follows a modal verb like 'please'
                # if token.head.pos_ == "INTJ" and token.head.lower_ == "please":
                #     return True
    return False



def count_syllables(text):
    # Process the text with spaCy
    doc = nlp_en(text)
    
    # Count syllables in each token that is a word
    syllable_count = sum(len(dic.inserted(token.text).split('-')) for token in doc if token.is_alpha)
    
    return syllable_count


if __name__ == '__main__':
    mbox = mailbox.mbox('email_data/Непрочитанные.mbox')
    output_directory = "/Users/viktorkertanov/Library/Mobile Documents/iCloud~md~obsidian/Documents/emails_for_poems"

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    imperatives = []
    # Iterate through all messages in the .mbox file
    for m_idx, message in enumerate(islice(mbox, 2500)):
        print(f'{m_idx} message is being processed.')
        try:
            subject = decode_email_header(message['subject'])
            sender = decode_email_header(message['from'])
        except:
            continue
        if 'thelonius19@gmail.com' in sender.lower() or '@facebookmail.com>' in sender.lower():
            continue
        date = decode_email_header(message['date'])

        # Extract email body
        try:
            msg = message_from_string(message.as_string())
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            continue
        body = extract_email_body(msg)
        if is_html_like_content(body) or not body:
            continue

        # Create markdown content
        formatted_date = format_date(date)
        len_subject = min(len(subject), 25)
        unique_identifier = sanitize_filename(f"{formatted_date}_{subject[:len_subject]}".replace(" ", "_"))
        filename = os.path.join(output_directory, f"{unique_identifier}.md")
        language = determine_language(message, body)
        language_hashtag = f"#{language}" if language else ""
        if language_hashtag != "#en":
            continue
        doc = nlp_en(body)

        for sent in doc.sents:
            if is_imperative(sent):
                words = sent.text.split(' ')
                len_text = len(words)
                max_len = np.min([len_text, 20])
                max_characters= 400
                
                text_to_append = ' '.join(words[:max_len]).replace('\n', ' ').replace('\r', '')
                max_chr = np.min([len(text_to_append)-1, max_characters])
                # syllables= count_syllables(text_to_append)
                imperatives.append(f'{m_idx}. {text_to_append[:max_chr]}')
                
    
    for el_idx, el in enumerate(imperatives, start=1):
        print(f'{el_idx}. {el}')
    
    filename = "cta_project/cta_raw.csv"

    # Write to the CSV file
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for el in imperatives:
            writer.writerow([el])
            

    print(f"Data saved to {filename}")
        
