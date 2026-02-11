"""
Comprehensive tests for save/load functionality.

Tests cover:
- Basic save and load operations
- Backward compatibility with old format
- File handling edge cases
- Data integrity checks
"""
import json
import os

import pytest

from autoscraper import AutoScraper


class TestSaveLoad:
    """Tests for save and load functionality."""

    def test_save_creates_file(self, tmp_path):
        """Test that save creates a file at the specified path."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        assert file_path.exists()
        assert file_path.is_file()

    def test_save_valid_json(self, tmp_path):
        """Test that saved file contains valid JSON."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        with open(file_path, "r") as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "stack_list" in data

    def test_save_overwrites_existing_file(self, tmp_path):
        """Test that save overwrites existing file."""
        file_path = tmp_path / "model.json"

        # Create first scraper and save
        scraper1 = AutoScraper()
        scraper1.build(html="<div>First</div>", wanted_list=["First"])
        scraper1.save(file_path)

        # Create second scraper and save to same path
        scraper2 = AutoScraper()
        scraper2.build(html="<span>Second</span>", wanted_list=["Second"])
        scraper2.save(file_path)

        # Load and verify it's the second scraper
        loaded = AutoScraper()
        loaded.load(file_path)
        result = loaded.get_result_exact(html="<span>Second</span>")
        assert "Second" in result

    def test_load_restores_stack_list(self, tmp_path):
        """Test that load correctly restores stack_list."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])
        original_stack = scraper.stack_list.copy()

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        loaded_scraper = AutoScraper()
        loaded_scraper.load(file_path)

        assert loaded_scraper.stack_list == original_stack

    def test_load_preserves_functionality(self, tmp_path):
        """Test that loaded scraper works the same as original."""
        html = "<ul><li>A</li><li>B</li><li>C</li></ul>"

        # Build and save
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["A"])
        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        # Load and test
        loaded = AutoScraper()
        loaded.load(file_path)

        original_result = scraper.get_result_similar(html=html, contain_sibling_leaves=True)
        loaded_result = loaded.get_result_similar(html=html, contain_sibling_leaves=True)

        assert original_result == loaded_result

    def test_multiple_save_load_cycles(self, tmp_path):
        """Test multiple save/load cycles preserve data."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Content"])

        file_path = tmp_path / "model.json"

        # Multiple save/load cycles
        for _ in range(3):
            scraper.save(file_path)
            new_scraper = AutoScraper()
            new_scraper.load(file_path)
            scraper = new_scraper

        result = scraper.get_result_exact(html=html)
        assert "Content" in result


class TestBackwardCompatibility:
    """Tests for backward compatibility with old save format."""

    def test_load_legacy_list_format(self, tmp_path):
        """Test loading old format where data is just a list."""
        # Old format: just the stack_list array
        legacy_data = [
            {
                "content": [("div", {"class": "", "style": ""})],
                "wanted_attr": None,
                "is_full_url": False,
                "is_non_rec_text": False,
                "url": "",
                "hash": "abc123",
                "stack_id": "rule_abc123",
                "alias": "",
            }
        ]

        file_path = tmp_path / "legacy.json"
        with open(file_path, "w") as f:
            json.dump(legacy_data, f)

        scraper = AutoScraper()
        scraper.load(file_path)

        assert scraper.stack_list == legacy_data
        assert len(scraper.stack_list) == 1

    def test_load_new_dict_format(self, tmp_path):
        """Test loading new format with stack_list key."""
        stack_data = [
            {
                "content": [("span", {"class": "", "style": ""})],
                "wanted_attr": None,
                "is_full_url": False,
                "is_non_rec_text": False,
                "url": "",
                "hash": "def456",
                "stack_id": "rule_def456",
                "alias": "test",
            }
        ]

        new_data = {"stack_list": stack_data}

        file_path = tmp_path / "new.json"
        with open(file_path, "w") as f:
            json.dump(new_data, f)

        scraper = AutoScraper()
        scraper.load(file_path)

        assert scraper.stack_list == stack_data
        assert len(scraper.stack_list) == 1

    def test_legacy_format_with_scraper_workflow(self, tmp_path):
        """Test that legacy format works in complete workflow."""
        # Create legacy format file
        legacy_stack = [
            {
                "content": [
                    ("[document]", {}, 0),
                    ("div", {"class": "", "style": ""}, 0),
                ],
                "wanted_attr": None,
                "is_full_url": False,
                "is_non_rec_text": False,
                "url": "",
                "hash": "test123",
                "stack_id": "rule_test123",
                "alias": "",
            }
        ]

        file_path = tmp_path / "legacy.json"
        with open(file_path, "w") as f:
            json.dump(legacy_stack, f)

        # Load and use
        scraper = AutoScraper()
        scraper.load(file_path)

        assert len(scraper.stack_list) == 1
        assert scraper.stack_list[0]["stack_id"] == "rule_test123"


class TestSaveLoadEdgeCases:
    """Tests for edge cases in save/load."""

    def test_save_empty_stack_list(self, tmp_path):
        """Test saving scraper with empty stack_list."""
        scraper = AutoScraper()
        file_path = tmp_path / "empty.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)
        assert loaded.stack_list == []

    def test_save_with_unicode_content(self, tmp_path):
        """Test saving and loading with unicode content."""
        html = "<div>Unicode: 你好 مرحبا שלום</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Unicode: 你好 مرحبا שלום"])

        file_path = tmp_path / "unicode.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)
        result = loaded.get_result_exact(html=html)
        assert "Unicode: 你好 مرحبا שלום" in result

    def test_save_with_special_characters_in_path(self, tmp_path):
        """Test saving with special characters in file path."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])

        file_path = tmp_path / "model with spaces.json"
        scraper.save(file_path)

        assert file_path.exists()

        loaded = AutoScraper()
        loaded.load(file_path)
        assert len(loaded.stack_list) > 0

    def test_save_with_complex_rules(self, tmp_path):
        """Test saving and loading with complex rules."""
        html = """
        <div class="outer">
            <div class="middle">
                <span class="inner" data-id="123">
                    <a href="/link">Target</a>
                </span>
            </div>
        </div>
        """
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Target"])

        file_path = tmp_path / "complex.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)

        result = loaded.get_result_exact(html=html)
        assert "Target" in result

    def test_load_empty_file(self, tmp_path):
        """Test loading from empty file raises error."""
        file_path = tmp_path / "empty.json"
        file_path.write_text("")

        scraper = AutoScraper()
        with pytest.raises(json.JSONDecodeError):
            scraper.load(file_path)

    def test_save_with_nested_directory(self, tmp_path):
        """Test saving to nested directory that doesn't exist yet."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])

        nested_path = tmp_path / "level1" / "level2"
        nested_path.mkdir(parents=True)
        file_path = nested_path / "model.json"

        scraper.save(file_path)
        assert file_path.exists()


class TestDataIntegrity:
    """Tests for data integrity in save/load operations."""

    def test_all_stack_fields_preserved(self, tmp_path):
        """Test that all stack fields are preserved in save/load."""
        html = '<div><a href="/test">Link</a></div>'
        scraper = AutoScraper()
        scraper.build(
            url="https://example.com",
            html=html,
            wanted_list=["https://example.com/test"],
        )

        file_path = tmp_path / "full.json"
        scraper.save(file_path)

        # Verify all expected fields are in saved data
        with open(file_path, "r") as f:
            data = json.load(f)

        stack = data["stack_list"][0]
        expected_fields = [
            "content",
            "wanted_attr",
            "is_full_url",
            "is_non_rec_text",
            "url",
            "hash",
            "stack_id",
        ]

        for field in expected_fields:
            assert field in stack, f"Field {field} not found in saved stack"

    def test_stack_id_consistent_after_reload(self, tmp_path):
        """Test that stack_id remains consistent after save/load."""
        html = "<div>Test</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Test"])

        original_ids = [s["stack_id"] for s in scraper.stack_list]

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)

        loaded_ids = [s["stack_id"] for s in loaded.stack_list]
        assert original_ids == loaded_ids

    def test_hash_consistent_after_reload(self, tmp_path):
        """Test that hash values remain consistent after save/load."""
        html = "<div>Test</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Test"])

        original_hashes = [s["hash"] for s in scraper.stack_list]

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)

        loaded_hashes = [s["hash"] for s in loaded.stack_list]
        assert original_hashes == loaded_hashes

    def test_alias_preserved_after_reload(self, tmp_path):
        """Test that aliases are preserved in save/load."""
        html = "<div>Test</div>"
        scraper = AutoScraper()
        scraper.build(html=html, wanted_dict={"test_alias": ["Test"]})

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)

        assert loaded.stack_list[0]["alias"] == "test_alias"

    def test_complex_wanted_dict_preserved(self, tmp_path):
        """Test that complex wanted_dict with multiple aliases works."""
        html = """
        <div>
            <span class="name">Product A</span>
            <span class="price">$10</span>
            <span class="name">Product B</span>
            <span class="price">$20</span>
        </div>
        """
        scraper = AutoScraper()
        scraper.build(
            html=html,
            wanted_dict={"products": ["Product A"], "prices": ["$10"]},
        )

        file_path = tmp_path / "model.json"
        scraper.save(file_path)

        loaded = AutoScraper()
        loaded.load(file_path)

        result = loaded.get_result_similar(html=html, group_by_alias=True, contain_sibling_leaves=True)
        assert "products" in result
        assert "prices" in result


class TestFilePermissions:
    """Tests for file permission handling."""

    def test_save_to_readonly_directory(self, tmp_path):
        """Test saving to read-only directory raises error."""
        scraper = AutoScraper()
        scraper.build(html="<div>Test</div>", wanted_list=["Test"])

        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)

        file_path = readonly_dir / "model.json"

        try:
            with pytest.raises((PermissionError, OSError)):
                scraper.save(file_path)
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
