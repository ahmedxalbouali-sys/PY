import itertools
import os


# COMMON PASSWORD BASE STRINGS
common_password_strings = [
    "password", "admin", "welcome", "login", "user", 
    "letmein", "iloveyou", "qwerty", "monkey", "dragon",
    "ahmed", "mohamed", "nour", "alex", "john",
    "tunisia", "tunis", "paris", "london",
    "qwert","qwerty","qwertyuiop","asdf","asdfgh","zxcv","zxcvbn",
    "123", "1995", "2000", "2020", "2024", "2025", "2026"
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

# ==========================================================
# HELPER FUNCTION: SIMPLE LEETSPEAK VARIANT GENERATOR
# ==========================================================
def simple_leet_variants(word):
    # ---------------------------------------------
    # Leetspeak substitution rules
    # Each letter maps to allowed replacements
    # ---------------------------------------------
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

    # ---------------------------------------------
    # Start with an empty base result
    # This allows progressive combination building
    # ---------------------------------------------
    results = set([""])

    # ---------------------------------------------
    # Process each character in the word
    # ---------------------------------------------
    for char in word.lower():

        # Temporary set to store new combinations
        next_results = set()

        # For every combination built so far
        for base in results:

            # If the character has leet substitutions
            if char in substitutions:
                for replacement in substitutions[char]:
                    # Append each replacement to the existing base
                    next_results.add(base + replacement)
            else:
                # If no substitution exists, keep the character as-is
                next_results.add(base + char)

        # Move to the next generation of combinations
        results = next_results

    return results
# ==========================================================
# MAIN FUNCTION: CUSTOM WORDLIST GENERATION
# ==========================================================
def generate_custom_wordlist(user_prompts, output_file="generated_wordlist.txt"):

    # --------------------------------------------------
    # Normalize and validate user input
    # --------------------------------------------------
    base_prompts = [p.strip() for p in user_prompts if p.strip()]
    if not base_prompts:
        raise ValueError("User prompts list is empty.")

    # Set ensures uniqueness of generated passwords
    generated = set()

    # ==================================================
    # 1) LEETSPEAK VARIANTS + CONNECTORS
    # ==================================================
    # Example: "alex" → a1ex, @lex, 4lex, etc.
    # Then: a1ex123, a1ex_, a1ex!
    for prompt in base_prompts:
        for variant in simple_leet_variants(prompt):
            generated.add(variant)

            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(variant + conn)
                    # Prefix variant intentionally omitted (design choice)

    # Extend prompt pool with newly generated variants
    extended_prompts = base_prompts + list(generated)

    # ==================================================
    # 2) CAPITALIZATION VARIANTS + CONNECTORS
    # ==================================================
    # Example: alex → Alex, ALEX, alex
    # Then: Alex123, _Alex, etc.
    for prompt in extended_prompts:
        for cap in capitalize_variants(prompt):
            generated.add(cap)

            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(cap + conn)
                    generated.add(conn + cap)

    # ==================================================
    # 3) FIRST-WORD CAPITALIZED COMBINATIONS
    # ==================================================
    # Example: alex + john → Alexjohn
    for prompt in extended_prompts:
        for other in extended_prompts:
            if prompt != other:
                generated.add(prompt.capitalize() + other)
                generated.add(other + prompt.capitalize())

    # ==================================================
    # 4) USER PROMPTS + COMMON PASSWORD STRINGS
    # ==================================================
    # Example: alex + 123 → alex_123, 123_alex, 123alex_
    for prompt in extended_prompts:
        for common in common_password_strings:
            for conn in common_password_connectors:
                if conn != "CapsShift":
                    generated.add(prompt + conn + common)
                    generated.add(common + conn + prompt)
                    generated.add(common + prompt + conn)

    # ==================================================
    # 5) CAPS SHIFT / CAMELCASE COMBINATIONS
    # ==================================================
    # Example: alex + john → alexJohn
    for first, second in itertools.permutations(extended_prompts, 2):
        generated.add(first.lower() + second.capitalize())

    # ==================================================
    # WRITE WORDLIST TO FILE
    # ==================================================
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

    # Write passwords respecting typical length constraints
    with open(output_file, "w", encoding="utf-8") as f:
        for word in sorted(generated):
            if 4 <= len(word) <= 32:
                f.write(word + "\n")


# EXAMPLE USAGE
if __name__ == "__main__":
    user_inputs = ["ahmed", "tunisia", "1999"]
    generate_custom_wordlist(user_inputs, output_file="custom_generated_wordlist.txt")

