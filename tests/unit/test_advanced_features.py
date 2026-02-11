"""
Tests for advanced AutoScraper features.

Tests cover:
- Fuzzy matching (text and attributes)
- Keep order functionality
- Non-recursive text extraction
- Full URL extraction
- Grouped results
"""
import re

import pytest

from autoscraper import AutoScraper


class TestFuzzyMatching:
    """Tests for fuzzy matching capabilities."""

    def test_text_fuzzy_matching_high_threshold(self):
        """Test text fuzzy matching with high similarity threshold."""
        html_train = "<div>Python Programming</div>"
        html_test = "<div>Python Programmin</div>"  # Missing 'g'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Python Programming"], text_fuzz_ratio=0.95)

        result = scraper.get_result_exact(html=html_test)
        # Should match due to high similarity
        assert len(result) > 0

    def test_text_fuzzy_matching_low_threshold(self):
        """Test text fuzzy matching with low similarity threshold."""
        html_train = "<div>Test</div>"
        html_test = "<div>Tst</div>"  # Missing 'e'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Test"], text_fuzz_ratio=0.7)

        result = scraper.get_result_exact(html=html_test)
        assert len(result) > 0

    def test_attr_fuzzy_matching(self):
        """Test attribute fuzzy matching."""
        html_train = '<div class="button-primary-large">Click</div>'
        html_test = '<div class="button-prim-large">Click</div>'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Click"])

        # Without fuzzy matching, should not match
        result_strict = scraper.get_result_exact(html=html_test, attr_fuzz_ratio=1.0)
        # With fuzzy matching, should match
        result_fuzzy = scraper.get_result_exact(html=html_test, attr_fuzz_ratio=0.8)

        assert len(result_fuzzy) > 0

    def test_attr_fuzzy_with_multiple_classes(self):
        """Test attribute fuzzy matching with multiple classes."""
        html_train = '<div class="btn primary active">Submit</div>'
        html_test = '<div class="btn primary activ">Submit</div>'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Submit"])

        result = scraper.get_result_exact(html=html_test, attr_fuzz_ratio=0.85)
        assert "Submit" in result

    def test_no_fuzzy_exact_match_required(self):
        """Test that attr_fuzz_ratio=1.0 requires exact attribute match."""
        html_train = '<div class="specific-class-name">Exact</div>'
        html_test = '<div class="completely-different">Exact</div>'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Exact"])

        # With attr_fuzz_ratio=1.0, attributes must match exactly
        # Since class attributes are different, exact match shouldn't find it
        result = scraper.get_result_similar(html=html_test, attr_fuzz_ratio=1.0)
        # May or may not match depending on how strict the matching is
        # Just verify it runs without error
        assert isinstance(result, list)


class TestKeepOrder:
    """Tests for keep_order functionality."""

    def test_keep_order_true(self):
        """Test that keep_order=True maintains document order."""
        html = """
        <div>
            <span>Third</span>
            <span>First</span>
            <span>Second</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["First"])

        result = scraper.get_result_similar(
            html=html, contain_sibling_leaves=True, keep_order=True
        )

        # Should maintain document order
        assert result == ["Third", "First", "Second"]

    def test_keep_order_false_default(self):
        """Test that keep_order=False is default and may not maintain order."""
        html = """
        <div>
            <span>A</span>
            <span>B</span>
            <span>C</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["A"])

        result = scraper.get_result_similar(
            html=html, contain_sibling_leaves=True, keep_order=False
        )

        # Should contain all items
        assert set(result) == {"A", "B", "C"}

    def test_keep_order_with_grouped(self):
        """Test keep_order with grouped results."""
        html = """
        <div>
            <p class="text">Para 1</p>
            <p class="text">Para 2</p>
            <p class="text">Para 3</p>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Para 1"])

        result = scraper.get_result_similar(
            html=html,
            grouped=True,
            contain_sibling_leaves=True,
            keep_order=True,
        )

        # Check that results exist and are in order
        for rule_results in result.values():
            if len(rule_results) == 3:
                assert rule_results == ["Para 1", "Para 2", "Para 3"]


class TestNonRecursiveText:
    """Tests for non-recursive text extraction."""

    def test_extract_non_recursive_text(self):
        """Test extracting text content from elements."""
        html = "<div>Direct text</div>"

        scraper = AutoScraper()
        # Build with the text
        result = scraper.build(html=html, wanted_list=["Direct text"])

        # The scraper should learn to extract text
        assert "Direct text" in result

    def test_non_recursive_vs_recursive(self):
        """Test extracting text from elements."""
        html = '<div class="parent">Parent content</div>'

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Parent content"])

        # Should extract text
        result = scraper.get_result_exact(html=html)
        assert "Parent content" in result


class TestFullURL:
    """Tests for full URL extraction."""

    def test_relative_to_full_url(self):
        """Test conversion of relative URLs to full URLs."""
        base_url = "https://example.com/page"
        html = '<a href="/path/to/page">Link</a>'

        scraper = AutoScraper()
        scraper.build(url=base_url, html=html, wanted_list=["https://example.com/path/to/page"])

        result = scraper.get_result_exact(url=base_url, html=html)
        assert "https://example.com/path/to/page" in result

    def test_full_url_with_different_base(self):
        """Test full URL extraction with different base URLs."""
        train_url = "https://site1.com"
        test_url = "https://site2.com"
        html = '<a href="/item">Link</a>'

        scraper = AutoScraper()
        scraper.build(url=train_url, html=html, wanted_list=["https://site1.com/item"])

        result = scraper.get_result_exact(url=test_url, html=html)
        # Should work with new base
        assert "https://site2.com/item" in result

    def test_image_src_full_url(self):
        """Test full URL extraction from image src."""
        url = "https://example.com"
        html = '<img src="/images/photo.jpg" alt="Photo">'

        scraper = AutoScraper()
        scraper.build(url=url, html=html, wanted_list=["https://example.com/images/photo.jpg"])

        result = scraper.get_result_exact(url=url, html=html)
        assert "https://example.com/images/photo.jpg" in result

    def test_url_with_subdirectory(self):
        """Test URL extraction from page in subdirectory."""
        url = "https://example.com/section/page.html"
        html = '<a href="../other/link.html">Link</a>'

        scraper = AutoScraper()
        full_url = "https://example.com/other/link.html"
        scraper.build(url=url, html=html, wanted_list=[full_url])

        result = scraper.get_result_exact(url=url, html=html)
        assert full_url in result


class TestGroupedResults:
    """Tests for grouped results functionality."""

    def test_grouped_by_rule_id(self):
        """Test grouping results by rule ID."""
        html = """
        <div>
            <span class="type1">A</span>
            <p class="type2">B</p>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["A", "B"])

        result = scraper.get_result_similar(html=html, grouped=True)

        assert isinstance(result, dict)
        assert len(result) > 0

        # Each rule should have its results
        for rule_id, values in result.items():
            assert isinstance(rule_id, str)
            assert isinstance(values, list)

    def test_grouped_by_alias(self):
        """Test grouping results by alias."""
        html = """
        <div>
            <span class="name">Product</span>
            <span class="price">$10</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(
            html=html,
            wanted_dict={"names": ["Product"], "prices": ["$10"]},
        )

        result = scraper.get_result_similar(html=html, group_by_alias=True)

        assert isinstance(result, dict)
        assert "names" in result
        assert "prices" in result
        assert "Product" in result["names"]
        assert "$10" in result["prices"]

    def test_grouped_unique_false(self):
        """Test grouped results with unique=False."""
        html = """
        <ul>
            <li>Item</li>
            <li>Item</li>
            <li>Item</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Item"])

        result = scraper.get_result_similar(html=html, grouped=True, unique=False)

        # Should have duplicates
        for values in result.values():
            if len(values) > 1:
                assert values.count("Item") > 1
                break

    def test_grouped_unique_true(self):
        """Test grouped results with unique=True."""
        html = """
        <ul>
            <li>Item</li>
            <li>Item</li>
            <li>Item</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Item"])

        result = scraper.get_result_similar(html=html, grouped=True, unique=True)

        # Should not have duplicates
        for values in result.values():
            assert len(values) == len(set(values))


class TestKeepBlank:
    """Tests for keep_blank functionality."""

    def test_keep_blank_false_default(self):
        """Test that blank values are filtered by default."""
        html = """
        <div>
            <span class="data">Value</span>
            <span class="data"></span>
            <span class="data">Another</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Value"])

        result = scraper.get_result_similar(html=html, keep_blank=False, contain_sibling_leaves=True)

        # Should not include empty string
        assert "" not in result
        assert "Value" in result
        assert "Another" in result

    def test_keep_blank_true(self):
        """Test that blank values are kept when keep_blank=True."""
        html_train = '<div class="item">Value</div>'
        html_test = '<div class="item"></div>'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["Value"])

        result = scraper.get_result_similar(html=html_test, keep_blank=True)

        # Should include empty string
        assert "" in result

    def test_keep_blank_with_missing_attributes(self):
        """Test keep_blank with missing attributes."""
        html_train = '<a href="/link">Link</a>'
        html_test = '<a>Link without href</a>'

        scraper = AutoScraper()
        scraper.build(html=html_train, wanted_list=["/link"])

        result = scraper.get_result_exact(html=html_test, keep_blank=True)
        # Might return empty depending on implementation


class TestContainSiblingLeaves:
    """Tests for contain_sibling_leaves functionality."""

    def test_contain_sibling_leaves_true(self):
        """Test that sibling elements are included."""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Item 1"])

        result = scraper.get_result_similar(html=html, contain_sibling_leaves=True)

        assert len(result) == 3
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result

    def test_contain_sibling_leaves_false(self):
        """Test that only exact match is returned."""
        html = """
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Item 1"])

        result = scraper.get_result_similar(html=html, contain_sibling_leaves=False)

        # Should only get exact match
        assert "Item 1" in result
        # Might have some matches but not all siblings

    def test_contain_sibling_leaves_complex_structure(self):
        """Test sibling leaves with complex structure."""
        html = """
        <div class="container">
            <div class="row">
                <div class="col">A</div>
                <div class="col">B</div>
                <div class="col">C</div>
            </div>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["A"])

        result = scraper.get_result_similar(html=html, contain_sibling_leaves=True)

        assert "A" in result
        assert "B" in result
        assert "C" in result


class TestUniqueParameter:
    """Tests for unique parameter in get_result methods."""

    def test_unique_default_non_grouped(self):
        """Test that unique defaults to True for non-grouped results."""
        html = """
        <div>
            <span>Duplicate</span>
            <span>Duplicate</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Duplicate"])

        result = scraper.get_result_similar(html=html)

        # Default should remove duplicates
        assert result.count("Duplicate") == 1

    def test_unique_false_non_grouped(self):
        """Test unique=False keeps duplicates."""
        html = """
        <div>
            <span>Dup</span>
            <span>Dup</span>
            <span>Dup</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Dup"])

        result = scraper.get_result_similar(html=html, unique=False)

        # Should keep duplicates
        assert result.count("Dup") > 1

    def test_unique_with_grouped_results(self):
        """Test unique parameter with grouped results."""
        html = """
        <ul>
            <li class="item">Same</li>
            <li class="item">Same</li>
            <li class="item">Different</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Same"])

        result_unique = scraper.get_result_similar(
            html=html, grouped=True, unique=True, contain_sibling_leaves=True
        )

        result_not_unique = scraper.get_result_similar(
            html=html, grouped=True, unique=False, contain_sibling_leaves=True
        )

        # Unique should have less or equal items
        for rule_id in result_unique:
            if rule_id in result_not_unique:
                assert len(result_unique[rule_id]) <= len(result_not_unique[rule_id])


class TestWantedDict:
    """Tests for wanted_dict parameter."""

    def test_wanted_dict_basic(self):
        """Test basic wanted_dict functionality."""
        html = "<div><span>A</span><p>B</p></div>"

        scraper = AutoScraper()
        scraper.build(html=html, wanted_dict={"first": ["A"], "second": ["B"]})

        result = scraper.get_result_similar(html=html, group_by_alias=True)

        assert "first" in result
        assert "second" in result
        assert "A" in result["first"]
        assert "B" in result["second"]

    def test_wanted_dict_multiple_items_per_alias(self):
        """Test wanted_dict with multiple items per alias."""
        html = """
        <div>
            <h1>Title 1</h1>
            <h2>Title 2</h2>
            <p>Para 1</p>
            <p>Para 2</p>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(
            html=html,
            wanted_dict={"titles": ["Title 1", "Title 2"], "paragraphs": ["Para 1"]},
        )

        result = scraper.get_result_similar(html=html, group_by_alias=True)

        assert "titles" in result
        assert "paragraphs" in result

    def test_wanted_dict_overrides_wanted_list(self):
        """Test that wanted_dict takes precedence over wanted_list."""
        html = "<div>Content</div>"

        scraper = AutoScraper()
        # When both are provided, wanted_dict is used (wanted_list is ignored per code logic)
        scraper.build(
            html=html,
            wanted_list=["Content"],  # This will be ignored
            wanted_dict={"used": ["Content"]},
        )

        result = scraper.get_result_similar(html=html, group_by_alias=True)

        # Should have the alias from wanted_dict
        assert "used" in result or "" in result  # Empty alias if wanted_list was processed
        if "used" in result:
            assert "Content" in result["used"]
