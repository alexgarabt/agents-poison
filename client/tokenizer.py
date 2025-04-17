from typing import TypedDict 
from collections import Counter
from tree import TrieTree
import re


class WordInfo(TypedDict):
    tokens: list[str]  # List with tokens of the word in order
    frequency: int     # Frequency of appearance of the word

class BPETokenizer:
    corpus: list[str]       # Raw string with all the corpus for the tokenizer
    V: set[str]             # Vocabulary with all the tokens learned
    D: dict[str, WordInfo]  # Dictionary of the corpus
    """
        Dictionary with frecuencys of each word and the word divided in tokens
        Example
        {
            "lowest": {
                "tokens":  ["l", "o", "w", "e", "s", "t", "EOW"],
                "frequency": 2
            }
        }
    """

    EOW = "\uE000"
    """End of Word character, unicode char from private area"""

    def __init__(self, corpus_raw:str, t_vocabulary_size=1000, learn_callback=None):
        """
            Initilize the BPE tokenizer and learns the vocabulary of tokens from the corpus
            then is able to segementate new text into the token vocabulary created

            Parameters:
                corpus_raw:
                    The corpus text from where to learn the token vocabulary

                t_vocabulary_size: = 10K tokens
                    Its tells how much bigger should be the vocabulary =>
                    Target vocabulary size - initial vocabulary size
                    K(merges) = t_v_size - i_v_size

                learn_callback:
                    Callback called in each merge of the learn loop with the data of each iteration
        """
        # Format the the into a list of words, using white-space as word boundaries
        self.corpus = re.split(r"\s+", corpus_raw.strip())

        # Initialize the Dictionary with the corpus data
        self.D = {}
        for word in self.corpus:
            if word in self.D: 
                self.D[word]["frequency"] += 1 
            else:
                tokens = [c for c in word]
                # Add the End Of Word token to match ends more easy
                tokens.append(self.EOW)
                self.D[word] = {"tokens": tokens, "frequency": 1}

        # Initial set of tokens
        self.V: set[str] = {
            token
            for word_info in self.D.values()
            for token in word_info["tokens"]
        }

        # Calculate the number of merges for the LEARN step
        k: int =  t_vocabulary_size - len(self.V)

        # Learn the token vocabulary from the corpus
        self.__learn_BPE(k, callback=learn_callback)

        # Initialize the vocabulary tree
        self.tree_v = TrieTree(self.V)


    def get_token_vocabulary(self):
        return self.V

    def get_token_dictionary(self):
        return self.D

    def __learn_BPE(self, k: int, callback = None):
        """
        Function [BPE] BYTE-PAIR ENCODING implementation from 'Speech and Language Processing (2024)',
        Takes raw training corpus (separated into words by white space) and resturns a vocabulary/set 
        of tokens.
    
        The BPE token learner begins
        with a vocabulary that is just the set of all individual characters. It then examines the
        training corpus, chooses the two symbols that are most frequently adjacent (say ‘A’,
        ‘B’), adds a new merged symbol ‘AB’ to the vocabulary, and replaces every adjacent
        ’A’ ’B’ in the corpus with the new ‘AB’. It continues to count and merge, creating
        new longer and longer character strings, until k merges have been done creating
        k novel tokens;
    
        If (k) is big enough for a corpus then the token vocabulary for most of the words there will be a
        token except the rare ones that will be divided in various tokens
    
    
        PARAMATERS:
            k: int
                Number of merges, Vocabulary = set(orgininal chars) + k(new symbols).

            callback: function
                Function that is called on every iteration of the merge loop
    
        RETURN:
            Adds the new learned tokens to the vocabulary
        """
        for i in range(k):
            # Call thte callba
            if callback: callback(i=i, k=k, v=self.V, d=self.D)

            (t_l, t_r) = self.__get_most_frequent_pair(self.V, self.D)       # Get the most frequent pair of tokens in D
            if t_l == "" and t_r == "":
                # it doesnt found more tokens to merge
                break
            t_new = t_l + t_r                                              # Make a new token by concatenating
            self.V.add(t_new)                                              # Update the vocabulary
            self.__replace_each_ocurrence(self.D, (t_l, t_r), t_new)         # Upade the corpus to use the new token

    def __get_most_frequent_pair(self, V: set[str], D: dict[str, WordInfo]) -> tuple[str, str]:
        """
            Return the most frequent pair of adjacents tokens(V) in the corpus(D)
        """
        pair_counts = Counter()
        for info in D.values():
            tokens = info["tokens"]
            # count pairs of adjacent tokens
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                # only count if pair is in V or if you allow partial merges
                if pair[0] in V and pair[1] in V:
                    pair_counts[pair] += info["frequency"]
    
        if not pair_counts:
            # fallback, if no pairs found (could happen if corpus is too small)
            return ("", "")
    
        return pair_counts.most_common(1)[0][0]  # return the pair (e.g. ('l','o'))
    
    def __replace_each_ocurrence(self, D: dict[str, WordInfo], t_pair: tuple[str, str], t_new: str) -> None:
        """
            Replace the pair of tokens(t_pair) for new token(t_new) in the corpus (D)
        """
        t_l, t_r = t_pair
        for info in D.values():
            tokens = info["tokens"]
            i = 0
            new_tokens = []
            while i < len(tokens):
                # Check if the current token & the next token form the pair
                if i < len(tokens) - 1 and tokens[i] == t_l and tokens[i + 1] == t_r:
                    new_tokens.append(t_new)
                    i += 2  # skip the next token as it’s merged
                else:
                    new_tokens.append(tokens[i])
                    i += 1
            info["tokens"] = new_tokens

    def segment_word(self, word: str) -> list[str]:
        """
        Function [BPE] BYTE-PAIR ENCODING segmenter
        Segment a single word into subword tokens of the BPE learned vocabulary, using a greedy
        left-to-right matching approach.
        
        Parameters
            word: The word/string to segment SHOULD contain as final character the EOW

        return: A list of tokens.
        """
        tokens = []
        i = 0
        n = len(word)
        
        while i < n:
            node = self.tree_v.root
            j = i
            last_valid = -1  # records the furthest position where we found a valid token
    
            # Move forward character by character if there's a matching child in the trie
            while j < n and word[j] in node.children:
                node = node.children[word[j]]
                j += 1
                # If this node corresponds to a valid subword, update last_valid
                if node.is_token:
                    last_valid = j
    
            if last_valid != -1:
                # We found a valid subword that ends at position last_valid
                tokens.append(word[i:last_valid])
                i = last_valid  # jump forward to the end of that subword
            else:
                # No valid subword found for the first character
                # You can treat the single character as a fallback token
                tokens.append(word[i])
                i += 1
    
        return tokens

    def segment_string(self, string: str) -> list[str]:
        """
        Segmente the given string into the vocabulary tokens learned during the BPE learn fase
        """
        list_tokens = []
        formated: list[str] = re.split(r"\s+", string.strip())
        [list_tokens.extend(self.segment_word(word + self.EOW)) for word in formated]
        return list_tokens


