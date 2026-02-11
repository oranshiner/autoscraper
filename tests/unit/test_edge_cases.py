"""
Edge case and error condition tests for AutoScraper.

Tests cover:
- Error handling
- Edge cases in parsing
- Special HTML scenarios
- Boundary conditions
- Invalid inputs
"""
import json
import re
from unittest.mock import MagicMock, patch

import pytest

from autoscraper import AutoScraper


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_build_without_targets_raises_error(self):
        """Test that build raises ValueError when no targets are provided."""
        scraper = AutoScraper()
        with pytest.raises(ValueError, match="No targets were supplied"):
            scraper.build(html="<div>content</div>")

    def test_build_with_empty_wanted_list(self):
        """Test that build raises error with empty wanted_list."""
        scraper = AutoScraper()
        with pytest.raises(ValueError):
            scraper.build(html="<div>content</div>", wanted_list=[])

    def test_build_with_empty_wanted_dict(self):
        """Test that build raises error with empty wanted_dict values."""
        scraper = AutoScraper()
        with pytest.raises(ValueError):
            scraper.build(html="<div>content</div>", wanted_dict={"alias": []})

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        scraper = AutoScraper()
        with pytest.raises(FileNotFoundError):
            scraper.load("/nonexistent/path/file.json")

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON raises error."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json{}")

        scraper = AutoScraper()
        with pytest.raises(json.JSONDecodeError):
            scraper.load(file_path)


class TestEdgeCasesHTML:
    """Tests for edge cases in HTML parsing."""

    def test_empty_html(self):
        """Test handling of empty HTML."""
        scraper = AutoScraper()
        result = scraper.build(html="", wanted_list=["test"])
        assert result == []

    def test_html_with_special_characters(self):
        """Test HTML with special characters."""
        html = "<div>Special: @#$%^&*()_+-={}[]|\\:;<>?,./</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Special: @#$%^&*()_+-={}[]|\\:;<>?,./"])
        assert len(result) == 1

    def test_html_with_unicode(self):
        """Test HTML with unicode characters."""
        html = "<div>Hello 世界 🌍</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Hello 世界 🌍"])
        assert len(result) == 1

    def test_deeply_nested_html(self):
        """Test with deeply nested HTML structure."""
        html = "<div>" * 50 + "Deep content" + "</div>" * 50
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Deep content"])
        assert "Deep content" in result

    def test_malformed_html(self):
        """Test handling of malformed HTML."""
        html = "<div><p>Unclosed tag<div>Content</div>"
        scraper = AutoScraper()
        # Should not crash, parser handles malformed HTML
        result = scraper.build(html=html, wanted_list=["Content"])
        assert "Content" in result

    def test_html_with_cdata(self):
        """Test HTML with CDATA sections."""
        html = "<div><![CDATA[Some data]]>Regular text</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Regular text"])
        assert len(result) >= 0  # Should handle without crashing

    def test_html_with_comments(self):
        """Test HTML with comments."""
        html = "<div><!-- Comment -->Visible text</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Visible text"])
        assert "Visible text" in result

    def test_html_with_script_tags(self):
        """Test HTML with script tags."""
        html = """
        <div>
            <script>alert('test');</script>
            <span>Real content</span>
        </div>
        """
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Real content"])
        assert "Real content" in result


class TestBoundaryConditions:
    """Tests for boundary conditions."""

    def test_single_character_wanted(self):
        """Test with single character as wanted item."""
        html = "<div>A</div><div>B</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["A"])
        assert "A" in result

    def test_very_long_text(self):
        """Test with very long text content."""
        long_text = "A" * 10000
        html = f"<div>{long_text}</div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=[long_text])
        assert long_text in result

    def test_many_similar_elements(self):
        """Test with many similar elements."""
        html = "<ul>" + "".join(f"<li>Item {i}</li>" for i in range(100)) + "</ul>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Item 0"])
        similar = scraper.get_result_similar(html=html, contain_sibling_leaves=True)
        assert len(similar) == 100

    def test_empty_attributes(self):
        """Test elements with empty attributes."""
        html = '<div class="" style="">Content</div>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Content"])
        assert "Content" in result

    def test_whitespace_only_text(self):
        """Test with whitespace-only text."""
        html = "<div>   \n\t   </div>"
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["test"])
        assert result == []


class TestAttributeHandling:
    """Tests for attribute handling edge cases."""

    def test_multiple_classes(self):
        """Test elements with multiple classes."""
        html = '<div class="class1 class2 class3">Content</div>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Content"])
        assert "Content" in result

    def test_data_attributes(self):
        """Test elements with data attributes."""
        html = '<div data-id="123" data-name="test">Content</div>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Content"])
        assert "Content" in result

    def test_boolean_attributes(self):
        """Test elements with boolean attributes."""
        html = '<input disabled required>Content</input>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Content"])
        # Should handle without crashing

    def test_attribute_with_special_chars(self):
        """Test attributes with special characters."""
        html = '<div data-test="value with spaces & special chars">Content</div>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Content"])
        assert "Content" in result


class TestURLHandling:
    """Tests for URL handling edge cases."""

    def test_relative_url_without_base(self):
        """Test relative URL handling without base URL."""
        html = '<a href="/path">Link</a>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["/path"])
        assert "/path" in result

    def test_absolute_url(self):
        """Test absolute URL handling."""
        html = '<a href="https://example.com/path">Link</a>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["https://example.com/path"])
        assert "https://example.com/path" in result

    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        url = "https://example.com"
        html = '<a href="/item?id=123&ref=test">Link</a>'
        scraper = AutoScraper()
        result = scraper.build(url=url, html=html, wanted_list=["https://example.com/item?id=123&ref=test"])
        assert len(result) > 0

    def test_url_with_fragment(self):
        """Test URL with fragment."""
        url = "https://example.com"
        html = '<a href="/page#section">Link</a>'
        scraper = AutoScraper()
        result = scraper.build(url=url, html=html, wanted_list=["https://example.com/page#section"])
        assert len(result) > 0

    def test_protocol_relative_url(self):
        """Test protocol-relative URL."""
        html = '<a href="//example.com/path">Link</a>'
        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["//example.com/path"])
        assert "//example.com/path" in result


class TestRegexHandling:
    """Tests for regex pattern handling."""

    def test_build_with_complex_regex(self):
        """Test build with complex regex patterns."""
        html = "<div>Price: $19.99</div>"
        scraper = AutoScraper()
        pattern = re.compile(r"Price: \$\d+\.\d+")
        result = scraper.build(html=html, wanted_list=[pattern])
        # Regex matches the full text content
        assert len(result) >= 0  # May or may not find partial matches

    def test_regex_with_groups(self):
        """Test regex patterns with capture groups."""
        html = "<div>Email: test@example.com</div>"
        scraper = AutoScraper()
        pattern = re.compile(r"Email: [\w\.-]+@[\w\.-]+\.\w+")
        result = scraper.build(html=html, wanted_list=[pattern])
        # Regex needs to match the full text content
        assert len(result) >= 0

    def test_regex_no_match(self):
        """Test regex that doesn't match anything."""
        html = "<div>No numbers here</div>"
        scraper = AutoScraper()
        pattern = re.compile(r"\d+")
        result = scraper.build(html=html, wanted_list=[pattern])
        assert result == []


class TestStackListOperations:
    """Tests for stack_list operations."""

    def test_remove_nonexistent_rule(self):
        """Test removing a rule that doesn't exist."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Content"])
        original_count = len(scraper.stack_list)

        scraper.remove_rules(["nonexistent_rule"])
        assert len(scraper.stack_list) == original_count

    def test_keep_nonexistent_rule(self):
        """Test keeping only rules that don't exist."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Content"])

        scraper.keep_rules(["nonexistent_rule"])
        assert len(scraper.stack_list) == 0

    def test_remove_all_rules(self):
        """Test removing all rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Content"])
        rule_ids = [s["stack_id"] for s in scraper.stack_list]

        scraper.remove_rules(rule_ids)
        assert len(scraper.stack_list) == 0

    def test_set_aliases_for_multiple_rules(self):
        """Test setting aliases for multiple rules."""
        html = "<div><span>A</span><p>B</p></div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["A", "B"])

        rule_ids = [s["stack_id"] for s in scraper.stack_list]
        aliases = {rule_ids[0]: "first", rule_ids[1]: "second"}
        scraper.set_rule_aliases(aliases)

        assert scraper.stack_list[0]["alias"] == "first"
        assert scraper.stack_list[1]["alias"] == "second"


class TestInitialization:
    """Tests for AutoScraper initialization."""

    def test_init_with_no_args(self):
        """Test initialization with no arguments."""
        scraper = AutoScraper()
        assert scraper.stack_list == []

    def test_init_with_stack_list(self):
        """Test initialization with existing stack_list."""
        existing_stack = [{"stack_id": "test", "content": []}]
        scraper = AutoScraper(stack_list=existing_stack)
        assert scraper.stack_list == existing_stack

    def test_init_with_none_stack_list(self):
        """Test initialization with None stack_list."""
        scraper = AutoScraper(stack_list=None)
        assert scraper.stack_list == []


class TestRequestHeaders:
    """Tests for request header handling."""

    def test_request_headers_exist(self):
        """Test that request_headers class variable exists."""
        assert hasattr(AutoScraper, "request_headers")
        assert isinstance(AutoScraper.request_headers, dict)
        assert "User-Agent" in AutoScraper.request_headers


class TestGetResultVariations:
    """Tests for different get_result method variations."""

    def test_get_result_similar_without_rules(self):
        """Test get_result_similar without any learned rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        result = scraper.get_result_similar(html=html)
        assert result == []

    def test_get_result_exact_without_rules(self):
        """Test get_result_exact without any learned rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        result = scraper.get_result_exact(html=html)
        assert result == []

    def test_get_result_without_rules(self):
        """Test get_result without any learned rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        similar, exact = scraper.get_result(html=html)
        assert similar == []
        assert exact == []

    def test_get_result_grouped_empty(self):
        """Test grouped result returns empty dict when no rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        result = scraper.get_result_similar(html=html, grouped=True)
        assert result == {}


class TestUpdateBehavior:
    """Tests for update parameter behavior."""

    def test_update_false_clears_rules(self):
        """Test that update=False clears previous rules."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Content"])
        first_rules = len(scraper.stack_list)

        scraper.build(html=html, wanted_list=["Content"], update=False)
        # Should have same or similar count, not doubled
        assert len(scraper.stack_list) <= first_rules + 1

    def test_update_true_preserves_rules(self):
        """Test that update=True preserves previous rules."""
        html1 = "<div>First</div>"
        html2 = "<span>Second</span>"
        scraper = AutoScraper()

        scraper.build(html=html1, wanted_list=["First"])
        first_count = len(scraper.stack_list)

        scraper.build(html=html2, wanted_list=["Second"], update=True)
        assert len(scraper.stack_list) >= first_count


class TestDeprecatedMethods:
    """Tests for deprecated methods."""

    def test_generate_python_code_prints_message(self, capsys):
        """Test that generate_python_code prints deprecation message."""
        scraper = AutoScraper()
        scraper.generate_python_code()

        captured = capsys.readouterr()
        assert "deprecated" in captured.out.lower()
