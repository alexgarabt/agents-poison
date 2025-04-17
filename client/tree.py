class TrieNode:
    """
    A node in the Trie tree, storing its children and a flag indicating
    if the path to this node corresponds to a valid token (subword)
    """
    def __init__(self):
        # Key: character, Value: TrieNode
        self.children: dict[str, "TrieNode"]  = {}
        # True the path from the root to this node represents token
        self.is_token: bool = False

class TrieTree:
    """
    A trie tree that supports inserting tokens (subwords)
    and segmenting new words with greedy longest match strategy.

    Example:
                   [*]
                 /  |  \
               [t] [a] [l]
              /     |     \
    "to" <= [o*]   [p]    [o*] => "lo
                    |        \
         "app" <= [p*]      [w*] => "low"
                    
    """

    root: TrieNode

    def __init__(self, token_vocabulary: set[str]):
        """
        Build the trie by inserting every token from the BPE vocabulary

        Parameter:
            token_vocabulary: The set of BPE tokens.
        """
        self.root = TrieNode()
        for token in token_vocabulary:
            self.insert(token)

    def insert(self, token: str) -> None:
        """
        Insert a single subword token into the trie.
        
        Parameter:
            token: The subword string to insert (e.g., "lo", "th", "lowest").
        """
        node = self.root
        for char in token:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_token = True
