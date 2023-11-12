def manacher(text):
    T = '#'.join('^{}$'.format(text))

    n = len(T)
    P = [0] * n
    C, R = 0, 0
    
    for i in range(1, n-1):
        mirr = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[mirr])
        
        while T[i + 1 + P[i]] == T[i - 1 - P[i]]:
            P[i] += 1
            
        if i + P[i] > R:
            C, R = i, i + P[i]
    
    max_length = max(P)
    center_index = P.index(max_length)
    start = (center_index - max_length) // 2
    end = start + max_length
    return text[start:end]

if __name__ == '__main__':

    b = manacher('''''')
    print(b)