from collections import OrderedDict
from difflib import SequenceMatcher
from typing import Any, List
import unicodedata


def unique_stack_list(stack_list: List[dict]) -> List[dict]:
    """
    Remove duplicate stacks based on their hash values.

    Args:
        stack_list: List of stack dictionaries, each containing a 'hash' key

    Returns:
        List of unique stack dictionaries, preserving order
    """
    seen = set()
    unique_list = []
    for stack in stack_list:
        stack_hash = stack['hash']
        if stack_hash in seen:
            continue
        unique_list.append(stack)
        seen.add(stack_hash)
    return unique_list


def unique_hashable(hashable_items: List[Any]) -> List[Any]:
    """
    Remove duplicates from the list while preserving order.

    Args:
        hashable_items: List of hashable items

    Returns:
        List with duplicates removed, preserving original order
    """
    return list(OrderedDict.fromkeys(hashable_items))


def get_non_rec_text(element: Any) -> str:
    """
    Get non-recursive text from a BeautifulSoup element.

    Args:
        element: BeautifulSoup element

    Returns:
        Text content without recursive children, stripped of whitespace
    """
    return ''.join(element.find_all(text=True, recursive=False)).strip()


def normalize(item: Any) -> Any:
    """
    Normalize text using Unicode NFKD normalization.

    Args:
        item: Item to normalize (typically a string)

    Returns:
        Normalized and stripped string if item is a string, otherwise returns item unchanged
    """
    if not isinstance(item, str):
        return item
    return unicodedata.normalize("NFKD", item.strip())


def text_match(t1: Any, t2: str, ratio_limit: float) -> bool:
    """
    Match two text values with optional fuzzy matching.

    Args:
        t1: First text value (string or compiled regex pattern)
        t2: Second text value (string)
        ratio_limit: Similarity ratio threshold (0.0 to 1.0).
                     1.0 means exact match, lower values allow fuzzy matching

    Returns:
        True if texts match according to the ratio limit, False otherwise
    """
    if hasattr(t1, 'fullmatch'):
        return bool(t1.fullmatch(t2))
    if ratio_limit >= 1:
        return t1 == t2
    return SequenceMatcher(None, t1, t2).ratio() >= ratio_limit


class ResultItem:
    """
    Container for scraped result items with their positions.

    Attributes:
        text: The scraped text content
        index: The index/position of the item in the document
    """

    def __init__(self, text: str, index: int) -> None:
        self.text = text
        self.index = index

    def __str__(self) -> str:
        return self.text


class FuzzyText:
    """
    Fuzzy text matching with configurable similarity threshold.

    Attributes:
        text: The text to match against
        ratio_limit: Similarity threshold (0.0 to 1.0)
        match: Placeholder for match results
    """

    def __init__(self, text: str, ratio_limit: float) -> None:
        self.text = text
        self.ratio_limit = ratio_limit
        self.match = None

    def search(self, text: str) -> bool:
        """
        Check if the given text matches with similarity above the threshold.

        Args:
            text: Text to compare against

        Returns:
            True if similarity ratio is above the threshold, False otherwise
        """
        return SequenceMatcher(None, self.text, text).ratio() >= self.ratio_limit
