import re

def clean_text(text):
    # Updated to include Cyrillic letters and handle both lower and upper case
    return re.sub(r'[^\w\s]', '', text).lower()

def manacher(text):
    cleaned_text = clean_text(text).replace(" ", "").replace("\n", "")
    T = '#'.join('^{}$'.format(cleaned_text))
    n = len(T)
    P = [0] * n
    C, R = 0, 0
    space_positions = [pos for pos, char in enumerate(clean_text(text)) if char in [" ", "\n"]]

    palindromes = []  # List to hold palindromes

    for i in range(1, n-1):
        mirr = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[mirr])

        while i + 1 + P[i] < n and i - 1 - P[i] >= 0 and T[i + 1 + P[i]] == T[i - 1 - P[i]]:
            P[i] += 1

        if i + P[i] > R:
            C, R = i, i + P[i]

        # If the palindrome has a length greater than 10, add it to the list
        if P[i] > 10:
            max_length = P[i]
            center_index = i
            start = (center_index - max_length) // 2
            end = start + max_length

            # Convert the indices back to include spaces
            cleaned_text_with_spaces = clean_text(text)
            for space_pos in space_positions:
                if space_pos <= start:
                    start += 1
                    end += 1
                elif space_pos < end:
                    end += 1

            palindromes.append(cleaned_text_with_spaces[start:end])

    return palindromes


if __name__ == '__main__':

    pal = manacher('''Кони, топот, инок,
Но не речь, а черен он.
Идем, молод, долом меди.
Чин зван мечем навзничь.
Голод, чем меч долог?
Пал, а норов худ и дух ворона лап.
А что? Я лов? Воля отча!
Яд, яд, дядя!
Иди, иди!
Мороз в узел, лезу взором.
Солов зов, воз волос.
Колесо. Жалко поклаж. Оселок.
Сани, плот и воз, зов и толп и нас.
Горд дох, ход дрог.
И лежу. — Ужели?
Зол, гол лог лоз.
И к вам и трем с смерти мавки.''')
    print(pal)