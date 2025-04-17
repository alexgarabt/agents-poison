from sys import argv
from tokenizer import BPETokenizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

def iteration_progress(i, k):
    """Display the progress of token learning as a percentage."""
    if i % 100 == 0:
        percentage = (i / k) * 100
        print(f"{percentage:.2f}%", end=", ...", flush=True)

def get_num_tokens():
    """Prompt the user to input the number of tokens to learn."""
    while True:
        try:
            return int(input("\nEnter number of tokens to learn (k) = "))
        except ValueError:
            print("Invalid input. Please enter an integer.")

def read_corpus(filename):
    """Read the corpus from the given filename."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None

def display_vocabulary(tokenizer, new_eow):
    """Display the learned token vocabulary if the user opts to."""
    show_v = input("Want to display the learned token vocabulary? [Y/N]: ").strip().upper()
    if show_v == "Y":
        tokens = [token.replace(BPETokenizer.EOW, new_eow) for token in list(tokenizer.V)]
        print("\nVOCABULARY:\n\n" + str(tokens) + "\n")

def tokenize_sentences(tokenizer, new_eow):
    """Prompt the user to tokenize sentences until they exit."""
    while True:
        print("\n-----------")
        sentence = input("Tokenize sentence => ").strip()
        if not sentence:
            print("Exiting...")
            break

        tokens = tokenizer.segment_string(sentence)
        tokens = [token.replace(BPETokenizer.EOW, new_eow) for token in tokens]
        print("\nTokens =>\n" + str(tokens))
        print("-----------\n")

def main():
    """Main function to learn and tokenize using BPE."""
    if len(argv) < 2:
        print("Usage: python client.py <filename>")
        return

    filename = argv[1]
    new_eow = "_"

    print(f"Learning token vocabulary from: {filename}")
    num_tokens = get_num_tokens()

    corpus = read_corpus(filename)
    if corpus is None:
        return

    print("\nLearning tokens", end=": ...")
    tokenizer = BPETokenizer(corpus, t_vocabulary_size=num_tokens, learn_callback=iteration_progress)
    print(f"\nVocabulary length = {len(tokenizer.V)}\n")

    display_vocabulary(tokenizer, new_eow)
    tokenize_sentences(tokenizer, new_eow)

if __name__ == "__main__":
    main()
