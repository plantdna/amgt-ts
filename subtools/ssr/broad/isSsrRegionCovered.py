import re
    
def is_ssr_region_covered(match_start, ssr_pos_left, ssr_pos_right, cigar):
    if match_start > ssr_pos_left:
        return False
    # end if, if ssr's left position is smaller than match start position, 
    # the SSR region on the locus' reference is not covered.
    
    # find the regex 
    pattern = r'(\d+)(\D)'
    r1 = re.findall(pattern, cigar)
    # r1 as: [('3', 'H'), ('43', 'M'), ('7', 'I'), ('80', 'M'), ('184', 'H')]
    
    occur_times  = 0
    ruler = match_start
    for size, action in r1:
        occur_times += 1
        
        if action == 'S':
            if occur_times == 1:
                continue
            else:
                ruler += int(size)
            # end if
            
        elif action in 'MID':
            ruler += int(size)
        # end if
        
    # end for
    
    if ruler < ssr_pos_right:
        return False
    else:
        return True

    
# end def
        