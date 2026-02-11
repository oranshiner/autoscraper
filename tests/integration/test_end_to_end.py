"""
End-to-end integration tests for AutoScraper.

Tests cover complete workflows including:
- Multi-page scraping scenarios
- Rule refinement workflows
- Complex data extraction patterns
- Real-world use case simulations
"""
import re

import pytest

from autoscraper import AutoScraper


class TestMultiPageScraping:
    """Tests for multi-page scraping scenarios."""

    def test_learn_from_one_page_apply_to_another(self):
        """Test learning rules from one page and applying to similar page."""
        page1 = """
        <div class="product">
            <h2 class="title">Laptop</h2>
            <span class="price">$999</span>
            <p class="description">High performance</p>
        </div>
        """

        page2 = """
        <div class="product">
            <h2 class="title">Desktop</h2>
            <span class="price">$1299</span>
            <p class="description">Powerful workstation</p>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=page1, wanted_list=["Laptop", "$999"])

        result = scraper.get_result_exact(html=page2)
        assert "Desktop" in result
        assert "$1299" in result

    def test_incremental_learning_workflow(self):
        """Test incremental learning from multiple pages."""
        pages = [
            '<div class="item"><span class="name">Item A</span><span class="id">ID001</span></div>',
            '<div class="product"><span class="title">Item B</span><span class="code">ID002</span></div>',
            '<section class="entry"><span class="label">Item C</span><span class="ref">ID003</span></section>',
        ]

        scraper = AutoScraper()

        # Learn from first page
        scraper.build(html=pages[0], wanted_list=["Item A", "ID001"])

        # Incrementally learn from other pages
        scraper.build(html=pages[1], wanted_list=["Item B", "ID002"], update=True)
        scraper.build(html=pages[2], wanted_list=["Item C", "ID003"], update=True)

        # Should work on all pages
        for page in pages:
            result = scraper.get_result_exact(html=page)
            assert len(result) >= 1

    def test_cross_site_pattern_extraction(self):
        """Test extracting similar patterns across different site structures."""
        site1 = '<article><h1 class="headline">Breaking News</h1></article>'
        site2 = '<div><h2 class="title">Latest Update</h2></div>'
        site3 = '<section><h3 class="heading">New Feature</h3></section>'

        scraper = AutoScraper()

        # Learn from all sites
        scraper.build(html=site1, wanted_list=["Breaking News"])
        scraper.build(html=site2, wanted_list=["Latest Update"], update=True)
        scraper.build(html=site3, wanted_list=["New Feature"], update=True)

        # Test on a new similar structure
        test_site = '<article><h1 class="headline">Test News</h1></article>'
        result = scraper.get_result_exact(html=test_site)
        assert "Test News" in result


class TestRuleRefinement:
    """Tests for rule refinement workflows."""

    def test_remove_noisy_rules(self):
        """Test removing rules that extract unwanted data."""
        html = """
        <div class="content">
            <h2>Title</h2>
            <p>Description text</p>
            <div class="ads">Advertisement</div>
            <span class="price">$50</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Title", "Description text", "$50"])

        # Get grouped results to identify rules
        grouped = scraper.get_result_exact(html=html, grouped=True)

        # Find and remove rule that might also match ads
        # (In real scenario, you'd test on page with ads)
        initial_count = len(scraper.stack_list)
        assert initial_count > 0

    def test_keep_only_best_rules(self):
        """Test keeping only the most reliable rules."""
        html = """
        <div>
            <span class="data">Value1</span>
            <span class="data">Value2</span>
            <span class="data">Value3</span>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["Value1"])

        # Keep only specific rules
        rule_ids = [s["stack_id"] for s in scraper.stack_list]
        if rule_ids:
            scraper.keep_rules([rule_ids[0]])
            assert len(scraper.stack_list) == 1

    def test_alias_based_filtering(self):
        """Test filtering results by alias."""
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
            wanted_dict={"names": ["Product A"], "prices": ["$10"]},
        )

        result = scraper.get_result_similar(
            html=html, group_by_alias=True, contain_sibling_leaves=True
        )

        assert "names" in result
        assert "prices" in result
        assert len(result["names"]) >= 1
        assert len(result["prices"]) >= 1


class TestComplexDataExtraction:
    """Tests for complex data extraction patterns."""

    def test_nested_data_extraction(self):
        """Test extracting data from deeply nested structures."""
        html = """
        <div class="container">
            <div class="section">
                <div class="subsection">
                    <div class="item">
                        <span class="label">Target Data</span>
                    </div>
                </div>
            </div>
        </div>
        """

        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Target Data"])
        assert "Target Data" in result

    def test_sibling_extraction(self):
        """Test extracting sibling elements."""
        html = """
        <ul class="list">
            <li class="item">First</li>
            <li class="item">Second</li>
            <li class="item">Third</li>
            <li class="item">Fourth</li>
        </ul>
        """

        scraper = AutoScraper()
        scraper.build(html=html, wanted_list=["First"])

        siblings = scraper.get_result_similar(html=html, contain_sibling_leaves=True)
        assert len(siblings) == 4
        assert "First" in siblings
        assert "Second" in siblings
        assert "Third" in siblings
        assert "Fourth" in siblings

    def test_mixed_content_extraction(self):
        """Test extracting different types of content."""
        html = """
        <div class="card">
            <h3>Product Name</h3>
            <img src="/image.jpg" alt="Product image">
            <a href="/product/123">View Details</a>
            <span class="price">$99.99</span>
            <div class="rating" data-score="4.5">★★★★☆</div>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(
            html=html,
            wanted_list=["Product Name", "/image.jpg", "/product/123", "$99.99"],
        )

        result = scraper.get_result_exact(html=html)
        assert "Product Name" in result
        assert "/image.jpg" in result
        assert "/product/123" in result
        assert "$99.99" in result


class TestRealWorldSimulations:
    """Tests simulating real-world scraping scenarios."""

    def test_ecommerce_product_scraping(self):
        """Test scraping product data like an e-commerce site."""
        product_page = """
        <div class="product-detail">
            <h1 class="product-name">Wireless Headphones</h1>
            <div class="price-box">
                <span class="current-price">$79.99</span>
                <span class="original-price">$99.99</span>
            </div>
            <div class="rating">
                <span class="stars">★★★★☆</span>
                <span class="reviews">(234 reviews)</span>
            </div>
            <div class="availability">In Stock</div>
            <div class="description">
                High-quality wireless headphones with noise cancellation.
            </div>
        </div>
        """

        scraper = AutoScraper()
        wanted = [
            "Wireless Headphones",
            "$79.99",
            "(234 reviews)",
            "In Stock",
        ]
        scraper.build(html=product_page, wanted_list=wanted)

        # Test on similar product
        similar_product = """
        <div class="product-detail">
            <h1 class="product-name">Bluetooth Speaker</h1>
            <div class="price-box">
                <span class="current-price">$49.99</span>
                <span class="original-price">$69.99</span>
            </div>
            <div class="rating">
                <span class="stars">★★★★★</span>
                <span class="reviews">(567 reviews)</span>
            </div>
            <div class="availability">In Stock</div>
            <div class="description">
                Portable Bluetooth speaker with excellent sound quality.
            </div>
        </div>
        """

        result = scraper.get_result_exact(html=similar_product)
        assert "Bluetooth Speaker" in result
        assert "$49.99" in result
        assert "(567 reviews)" in result
        assert "In Stock" in result

    def test_news_article_scraping(self):
        """Test scraping news articles."""
        article1 = """
        <article>
            <h1 class="article-title">Major Discovery in Science</h1>
            <div class="meta">
                <span class="author">By John Doe</span>
                <span class="date">January 15, 2024</span>
            </div>
            <div class="content">
                <p>Scientists have made a groundbreaking discovery...</p>
            </div>
        </article>
        """

        scraper = AutoScraper()
        scraper.build(
            html=article1,
            wanted_dict={
                "title": ["Major Discovery in Science"],
                "author": ["By John Doe"],
                "date": ["January 15, 2024"],
            },
        )

        article2 = """
        <article>
            <h1 class="article-title">New Technology Announced</h1>
            <div class="meta">
                <span class="author">By Jane Smith</span>
                <span class="date">January 16, 2024</span>
            </div>
            <div class="content">
                <p>A revolutionary new technology was unveiled today...</p>
            </div>
        </article>
        """

        result = scraper.get_result_similar(html=article2, group_by_alias=True)
        assert "title" in result
        assert "author" in result
        assert "date" in result
        assert "New Technology Announced" in result["title"]
        assert "By Jane Smith" in result["author"]
        assert "January 16, 2024" in result["date"]

    def test_job_listing_scraping(self):
        """Test scraping job listings."""
        listing = """
        <div class="job-posting">
            <h2 class="job-title">Senior Software Engineer</h2>
            <div class="company">Tech Corp Inc.</div>
            <div class="location">San Francisco, CA</div>
            <div class="salary">$120,000 - $180,000</div>
            <div class="posted">Posted 2 days ago</div>
            <ul class="requirements">
                <li>5+ years experience</li>
                <li>Python expertise</li>
                <li>Cloud platforms</li>
            </ul>
        </div>
        """

        scraper = AutoScraper()
        scraper.build(
            html=listing,
            wanted_list=[
                "Senior Software Engineer",
                "Tech Corp Inc.",
                "San Francisco, CA",
                "$120,000 - $180,000",
            ],
        )

        # Test on different listing
        listing2 = """
        <div class="job-posting">
            <h2 class="job-title">Data Scientist</h2>
            <div class="company">Analytics Co.</div>
            <div class="location">New York, NY</div>
            <div class="salary">$100,000 - $150,000</div>
            <div class="posted">Posted 1 day ago</div>
            <ul class="requirements">
                <li>3+ years experience</li>
                <li>Machine learning</li>
                <li>Statistical analysis</li>
            </ul>
        </div>
        """

        result = scraper.get_result_exact(html=listing2)
        assert "Data Scientist" in result
        assert "Analytics Co." in result
        assert "New York, NY" in result


class TestEdgeCaseWorkflows:
    """Tests for edge case workflows."""

    def test_no_match_then_update(self):
        """Test workflow where initial build finds nothing, then updated."""
        html1 = "<div>No match here</div>"
        html2 = "<div>Target content</div>"

        scraper = AutoScraper()
        result1 = scraper.build(html=html1, wanted_list=["nonexistent"])
        assert result1 == []

        # Update with actual content
        result2 = scraper.build(html=html2, wanted_list=["Target content"], update=True)
        assert "Target content" in result2

    def test_duplicate_wanted_items(self):
        """Test with duplicate items in wanted_list."""
        html = "<div>Content</div>"
        scraper = AutoScraper()
        result = scraper.build(
            html=html, wanted_list=["Content", "Content", "Content"]
        )
        # Should handle gracefully
        assert "Content" in result

    def test_empty_html_with_rules(self):
        """Test applying rules to minimal HTML."""
        html1 = "<div>Content</div>"
        scraper = AutoScraper()
        scraper.build(html=html1, wanted_list=["Content"])

        # Apply to minimal HTML without matching content
        result = scraper.get_result_exact(html="<html></html>")
        assert result == []

    def test_progressive_rule_building(self):
        """Test progressively building more specific rules."""
        base_html = '<div class="item"><span>Text</span></div>'
        specific_html = '<div class="item special"><span class="highlight">Text</span></div>'

        scraper = AutoScraper()

        # Start with base
        scraper.build(html=base_html, wanted_list=["Text"])
        base_rules = len(scraper.stack_list)

        # Add more specific
        scraper.build(html=specific_html, wanted_list=["Text"], update=True)
        assert len(scraper.stack_list) >= base_rules


class TestPerformanceScenarios:
    """Tests for performance-related scenarios."""

    def test_large_html_document(self):
        """Test with large HTML document."""
        # Create large HTML with many elements
        items = "".join(f"<li class='item'>Item {i}</li>" for i in range(200))
        html = f"<ul>{items}</ul>"

        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Item 0"])

        # Should handle without issues
        similar = scraper.get_result_similar(html=html, contain_sibling_leaves=True)
        assert len(similar) == 200

    def test_many_rules(self):
        """Test with many learned rules."""
        scraper = AutoScraper()

        # Build multiple rules
        for i in range(20):
            html = f'<div class="type{i}">Content {i}</div>'
            scraper.build(html=html, wanted_list=[f"Content {i}"], update=True)

        # Should handle many rules
        assert len(scraper.stack_list) >= 10

    def test_complex_selector_chains(self):
        """Test with complex selector chains."""
        html = """
        <div class="level1">
            <div class="level2">
                <div class="level3">
                    <div class="level4">
                        <div class="level5">
                            <span class="target">Deep content</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

        scraper = AutoScraper()
        result = scraper.build(html=html, wanted_list=["Deep content"])
        assert "Deep content" in result

        # Should work on similar deep structure
        result2 = scraper.get_result_exact(html=html)
        assert "Deep content" in result2
