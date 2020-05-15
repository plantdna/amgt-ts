import re

def cigar_resolved(match_start, ssr_pos_left, ssr_pos_right, cigar, motif_length):
    # find the regex
    pattern = r'(\d+)(\D)'
    r1 = re.findall(pattern, cigar)
    # r1 as: [('3', 'H'), ('43', 'M'), ('7', 'I'), ('80', 'M'), ('184', 'H')]


    resolve_type='M'
    type_length = 0

    ruler = match_start
    for size, action in r1:
        if action == 'S':
            continue
        elif action == 'M':
            ruler += int(size)
        elif action =='I':
            if ruler >= ssr_pos_left - motif_length and ruler <= ssr_pos_right + motif_length:
                resolve_type = 'I'
                type_length = int(size)
                break
            # end if
        elif action =='D':
            if ruler >= ssr_pos_left - motif_length and ruler <= ssr_pos_right + motif_length:
                resolve_type = 'D'
                type_length = int(size) * -1
                break
            # end if
            ruler += int(size)
        # end if

    # end for
    return (resolve_type, type_length)


# end def
