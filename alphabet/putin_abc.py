from db_handlers.query import pu_speech_processed, get_news_by_title_id, get_n_random_titles




if __name__ == '__main__':
    titles_idx = get_n_random_titles(100, min_len=20000)
    target_letter = 'я'
    final_letters = []
    for title_idx in titles_idx:
        # news = get_news_by_title_id(title_idx.title_id)
        pu_words = pu_speech_processed(title_idx.news_full).strip()
        pu_words_split = pu_words.split(' ')
        a_aux = [x for x in pu_words_split if x]
        letters = [f"{x}" for id_x, x in enumerate(a_aux) if x.lower()[0] == target_letter]
        final_letters += letters
    
    letters = sorted(set(final_letters))
    for l in letters:
        print(l)

    print('Hello world!')
