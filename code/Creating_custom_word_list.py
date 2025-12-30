import itertools
import os


# COMMON PASSWORD BASE STRINGS
common_password_strings = [
    "password", "admin", "welcome", "login", "user", "test",
    "letmein", "iloveyou", "qwerty", "monkey", "dragon",
    "ahmed", "mohamed", "nour", "alex", "john",
    "tunisia", "tunis", "paris", "london",
    "qwert","qwerty","qwertyuiop","asdf","asdfgh","zxcv","zxcvbn",
    "1990", "1995", "2000", "2020", "2024", "2025", "2026"
]

# COMMON PASSWORD CONNECTORS
common_password_connectors = [
    "1", "12", "123", "1234", "12345", "123456",
    "!", "@", "#", "$", "%", "^", "&", "*",
    "_", "-", ".",
    "01", "007", "2023", "2024",
    "__", "--", "..",
    "CapsShift"
]

# HELPER FUNCTION: CAPITALIZATION VARIANTS
def capitalize_variants(word):
    return {
        word.lower(),
        word.upper(),
        word.capitalize()
    }

# HELPER FUNCTION: SIMPLE LEETSPEAK VARIANTS
def simple_leet_variants(word):
    substitutions = {
        "a": ["a", "@", "4"],
        "e": ["e", "3"],
        "i": ["i", "1"],
        "o": ["o", "0"],
        "s": ["s", "$", "5"],
        "t": ["t", "7"],
        "l": ["l", "1"],
        "g": ["g", "9"],
    }

    results = set([""])
    for char in word.lower():
        next_results = set()
        for base in results:
            if char in substitutions:
                for replacement in substitutions[char]:
                    next_results.add(base + replacement)
            else:
                next_results.add(base + char)
        results = next_results

    return results

# MAIN FUNCTION: CUSTOM WORDLIST GENERATION
def generate_custom_wordlist(user_prompts, output_file="generated_wordlist.txt"):
    print("[Debug] Starting wordlist generation")
    
    base_prompts = [p.strip() for p in user_prompts if p.strip()]
    if not base_prompts:
        raise ValueError("User prompts list is empty.")

    generated = set()
    print(f"[Debug] Base prompts: {base_prompts}")

    # 1) LEETSPEAK VARIANTS
    for prompt in base_prompts:
        for variant in simple_leet_variants(prompt):
            generated.add(variant)
            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(variant + conn)
                    #generated.add(conn + variant)
    print(f"[Debug] Generated after leetspeak: {len(generated)} items")

    extended_prompts = base_prompts + list(generated)
    print(f"[Debug] Extended prompts length: {len(extended_prompts)}")

    # 2) SINGLE PROMPT + CAPITALIZATION + CONNECTORS
    for prompt in extended_prompts:
        for cap in capitalize_variants(prompt):
            generated.add(cap)
            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(cap + conn)
                    generated.add(conn + cap)
    print(f"[Debug] Generated after capitalization + connectors: {len(generated)} items")

    # 3) FIRST WORD CAPITALIZED COMBINATIONS
    for prompt in extended_prompts:
        for other in extended_prompts:
            if prompt != other:
                combined = prompt.capitalize() + other
                generated.add(combined)
    print(f"[Debug] Generated after first-word capitalization combinations: {len(generated)} items")

    # 4) USER PROMPT + COMMON PASSWORD STRINGS
    for prompt in extended_prompts:
        for common in common_password_strings:
            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(prompt + conn + common)
                    generated.add(common + conn + prompt)
                    generated.add(common + prompt + conn)
    print(f"[Debug] Generated after user+common string combinations: {len(generated)} items")

    # 6) CapsShift (camelCase) COMBINATIONS
    for first, second in itertools.permutations(extended_prompts, 2):
        generated.add(first.lower() + second.capitalize())
    print(f"[Debug] Generated after CapsShift (camelCase) combinations: {len(generated)} items")

    # WRITE WORDLIST TO FILE
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for word in sorted(generated):
            if 4 <= len(word) <= 32:
                f.write(word + "\n")
    print(f"[✓] Wordlist generated successfully: {output_file}")
    print(f"[✓] Total passwords generated: {len(generated)}")

# EXAMPLE USAGE
if __name__ == "__main__":
    user_inputs = ["ahmed", "tunisia", "1999"]
    generate_custom_wordlist(user_inputs, output_file="custom_generated_wordlist.txt")

