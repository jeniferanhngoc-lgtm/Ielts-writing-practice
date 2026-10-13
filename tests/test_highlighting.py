import html
import re
from ui.core_framework import highlighted_html


def test_highlights_scaffolds_preserves_text_and_escapes_html():
    source='The chart illustrates how many cars were produced. Overall, A rose, while B fell. <script>alert(1)</script>'
    rendered=highlighted_html(source)
    assert '<script>' not in rendered
    assert '>how many</strong>' in rendered
    assert '>while</strong>' in rendered
    assert html.unescape(re.sub('<[^>]*>','',rendered))==source


def test_no_substring_matches_or_changes_to_data():
    rendered=highlighted_html('Together, tomatoes totalled 1.4 million in 2010.')
    assert '<strong' not in rendered
    assert '1.4 million in 2010' in rendered
