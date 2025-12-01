"""
Exhaustive password generator (Option B)

Generates permutations / combinations of tokens, connectors, capitalization, and leetspeak variants.
Writes results to file incrementally to avoid memory blowup.

Be careful: combinatorial explosion is real. Use the parameters to limit output.
"""

import itertools
import os
from typing import List, Optional
from itertools import product, permutations

# --- Put your provided common lists here (shortened/kept as you gave them) ---
common_password_strings = [
#    "0","00","000","0000","00000","000000","00000000",
#    "1","11","111","1111","11111","111111",
#    "2","22","222","2222","222222",
#    "3","33","333","3333","333333",
#    "4","44","444","4444","444444",
#    "5","55","555","5555","555555",
#    "6","66","666","6666","666666",
#    "7","77","777","7777",
#    "8","88","888","8888","888888",
#    "9","99","999","9999","999999",
#    "10","11","12","13","21","69","96","99","101","121","131",
#    "1010","1212","6969","112233","123","1234","12345","123456",
#    "1234567","12345678","123456789","1234567890","123123","123321","159753",
#    "qwert","qwerty","qwertyuiop","asdf","asdfgh","zxcv","zxcvbn",
#    "1q2w3e","qazwsx","poiuytrewq","mnbvcxz","qwe","qwe123","1qaz2wsx",
#    "password","pass","passwd","mypassword","letmein","welcome","iloveyou",
#    "alex","maria","eva","anna","sophia","sara","david","daniel","michael",
#    "paris","london","roma","tokyo","madrid","miami","berlin","dubai",
#    "1970","1980","1990","2000","2010","2020","2021","2022","2023","2024",
#    "january","february","march","april","may","june","july","august",
#    "dog","cat","pizza","chocolate","cocacola","youtube","google","netflix",
    "fuckyou","shit","bitch","money","family","home","secret","magic","dream"
#    # ... you included many more - paste the full list you gave earlier
]

common_password_connectors = [
#    "1", "12", "123", "1234", "12345", "01", "02", "07", "09",
#    "69", "007", "911", "123123", "111", "222", "333", "999",
#    "1980", "1985", "1990", "1999", "2000", "2010", "2012", "2015",
#    "!", "@", "#", "$", "%", "&", "*", ".", "-", "_", "~",
#    "!!", "@@", "--", "__", "..", "**", "123!", "123@", "123#", "!23",
#    "@123", "2023!", "2024!", "0", "00", "o", "O", "@", "4", "$", "5",
#    "@1", "@12", "@123", "!1", "!01", "_1", "_01", "-1", "-123", ".1",
    ".01", "aa", "bb"
    # ... you included more - paste the full list you gave earlier if needed
]

# --- Leet mapping for generating leet variants ---
LEET_MAP = {
    "a": ["a", "A", "@", "4"],
    "b": ["b", "B", "8"],
    "e": ["e", "E", "3"],
    "i": ["i", "I", "1", "!"],
    "l": ["l", "L", "1", "!" ],
    "o": ["o", "O", "0"],
    "s": ["s", "S", "5", "$"],
    "t": ["t", "T", "7"]
}

def leet_variants(token: str, max_variants_per_token: int = 8) -> List[str]:
    """
    Generate leetspeak variations for a token, capped to max_variants_per_token.
    Strategy: for each character that has leet substitutions, create combinations
    but limit the number of produced variants to avoid uncontrolled explosion.
    """
    token = token.strip()
    choices = []
    for ch in token:
        lower = ch.lower()
        if lower in LEET_MAP:
            choices.append(LEET_MAP[lower])
        else:
            choices.append([ch, ch.upper()])  # allow original and uppercase
    
    # Create product of choices but cap total outputs
    variants = []
    for combo in product(*choices):
        variants.append("".join(combo))
        if len(variants) >= max_variants_per_token:
            break
    # Always include original forms
    if token not in variants:
        variants.insert(0, token)
    if token.capitalize() not in variants:
        variants.append(token.capitalize())
    return list(dict.fromkeys(variants))  # preserve order, remove duplicates

def cap_variants_list(lst: List[str], cap: int) -> List[str]:
    """Helper: trim list to cap while preserving order."""
    return lst[:cap] if cap and len(lst) > cap else lst

# --- Main generator function ---
def generate_exhaustive_wordlist(
    user_tokens: List[str],
    output_path: str,
    include_common_strings: bool = True,
    include_common_connectors: bool = True,
    max_terms: int = 3,
    allow_repeats: bool = False,
    include_leet: bool = True,
    leet_variants_per_token: int = 6,
    include_caps: bool = True,
    connector_as_prefix_suffix: bool = True,
    max_output: Optional[int] = 5_000_000
) -> dict:
    """
    Generate an exhaustive style wordlist and write to 'output_path' (text file).
    Parameters:
      - user_tokens: list of strings provided by user (most important)
      - output_path: file path to write results to (will be overwritten)
      - include_common_strings: add global common strings into token pool
      - include_common_connectors: use connectors between tokens
      - max_terms: max number of tokens combined (e.g., 1..3). Increasing this explodes output.
      - allow_repeats: whether the same token can repeat in a combination
      - include_leet: include leet variants for tokens
      - leet_variants_per_token: cap of leet variants generated per token
      - include_caps: include capitalization variants (Original, Capitalize, UPPER)
      - connector_as_prefix_suffix: also use connectors as prefix/suffix to tokens
      - max_output: stop after writing this many passwords (None = no cap)
    Returns:
      dict with stats: {'written': n, 'estimated_upper_bound': m, 'output_path': path}
    """
    # Build token pool
    pool = []
    # Add user tokens first (highest priority)
    pool.extend([t.strip() for t in user_tokens if t.strip()])
    if include_common_strings:
        # append common strings but avoid duplicates
        for s in common_password_strings:
            if s not in pool:
                pool.append(s)

    # Build connectors
    connectors = [""]  # empty connector option
    if include_common_connectors:
        connectors.extend(common_password_connectors)

    # For each token prepare its variant list (caps / leet)
    token_to_variants = {}
    for tok in pool:
        variants = [tok]
        if include_caps:
            caps = [tok.capitalize(), tok.upper()]
            for c in caps:
                if c not in variants:
                    variants.append(c)
        if include_leet:
            leet_vars = leet_variants(tok, max_variants_per_token=leet_variants_per_token)
            for lv in leet_vars:
                if lv not in variants:
                    variants.append(lv)
        # cap each token's variant list to reasonable size to avoid insane blowup
        token_to_variants[tok] = cap_variants_list(variants, 12)

    # helper to yield variant strings for a token (original token string used to lookup variants)
    def variants_for_token(tok):
        return token_to_variants.get(tok, [tok])

    # Prepare order generator (permutations or product)
    total_written = 0
    total_estimated_upper = 0  # coarse estimate
    pool_tokens = pool  # list of base tokens (not variants)

    # Quick conservative estimate (may be huge)
    try:
        est = 0
        for k in range(1, max_terms+1):
            n = len(pool_tokens)
            if allow_repeats:
                combos = n ** k
            else:
                combos = 0
                if n >= k:
                    # permutations
                    combos = 1
                    for i in range(k):
                        combos *= (n - i)
            # each combo gets (avg_variant_count^k) variants and connector choices:
            avg_variants = sum(len(token_to_variants[t]) for t in pool_tokens) / max(1, len(pool_tokens))
            connector_choices = (len(connectors) if include_common_connectors else 1) ** max(0, k-1)
            # also consider prefix/suffix
            prefix_suffix_choices = (len(connectors) if connector_as_prefix_suffix else 1) ** 2
            est += combos * (avg_variants ** k) * connector_choices * prefix_suffix_choices
        total_estimated_upper = int(min(est, 10**18))  # avoid overflow
    except Exception:
        total_estimated_upper = -1

    # Write to file streaming
    written = 0
    with open(output_path, "w", encoding="utf-8", errors="ignore") as out_f:
        # for each length
        for k in range(1, max_terms + 1):
            # create sequences of base tokens
            if allow_repeats:
                seq_iter = product(pool_tokens, repeat=k)
            else:
                # permutations: order matters, no repeats
                seq_iter = permutations(pool_tokens, k)

            for seq in seq_iter:
                # Build all variant combinations for each token in seq
                variant_lists = [variants_for_token(tok) for tok in seq]

                # iterate over variant product
                for variant_combo in product(*variant_lists):
                    # connectors between tokens (k-1 positions)
                    if k == 1:
                        # single token; still consider prefix/suffix connectors if enabled
                        base = variant_combo[0]
                        # prefix/suffix options
                        if connector_as_prefix_suffix and include_common_connectors:
                            for pre in connectors:
                                for suf in connectors:
                                    if pre == "" and suf == "":
                                        s = base
                                    else:
                                        s = f"{pre}{base}{suf}"
                                    out_f.write(s + "\n")
                                    written += 1
                                    if max_output and written >= max_output:
                                        return {'written': written, 'estimated_upper_bound': total_estimated_upper, 'output_path': output_path}
                        else:
                            out_f.write(base + "\n")
                            written += 1
                            if max_output and written >= max_output:
                                return {'written': written, 'estimated_upper_bound': total_estimated_upper, 'output_path': output_path}
                    else:
                        # k >= 2: handle connectors between tokens
                        connector_positions = k - 1
                        # choose connector for each gap
                        for connector_choice in product(connectors, repeat=connector_positions):
                            # build string by interleaving variant tokens and connectors
                            parts = []
                            for i in range(k):
                                parts.append(variant_combo[i])
                                if i < connector_positions:
                                    parts.append(connector_choice[i])
                            candidate = "".join(parts)
                            out_f.write(candidate + "\n")
                            written += 1
                            if max_output and written >= max_output:
                                return {'written': written, 'estimated_upper_bound': total_estimated_upper, 'output_path': output_path}

                            # Also try adding prefix/suffix connectors around the whole candidate if enabled
                            if connector_as_prefix_suffix and include_common_connectors:
                                for pre in connectors:
                                    for suf in connectors:
                                        if pre == "" and suf == "":
                                            continue  # already wrote bare candidate
                                        s2 = f"{pre}{candidate}{suf}"
                                        out_f.write(s2 + "\n")
                                        written += 1
                                        if max_output and written >= max_output:
                                            return {'written': written, 'estimated_upper_bound': total_estimated_upper, 'output_path': output_path}

                # end variant combo loop
            # end seq loop
    # finished
    return {'written': written, 'estimated_upper_bound': total_estimated_upper, 'output_path': output_path}





# Example usage:    
user_tokens = ["nour", "ahmed", "test", "2025"]
result = generate_exhaustive_wordlist(
    user_tokens=user_tokens,
    output_path="generated_exhaustive_wordlist.txt",
    include_common_strings=True,
    include_common_connectors=True,
    max_terms=3,               # 1..3 tokens combined (increase at your own risk)
    allow_repeats=False,
    include_leet=True,
    leet_variants_per_token=4, # reduce to limit explosion
    include_caps=True,
    connector_as_prefix_suffix=True,
    max_output=2000000         # safety cap; set None to remove cap (dangerous)
)
print(result)
