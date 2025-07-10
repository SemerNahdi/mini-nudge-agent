import pytest
from unittest.mock import Mock, patch
from app.core.classifier import detect_tone, map_emotion_to_tone, init_tone_classifier

@pytest.fixture
def mock_classifier():
    """Fixture to mock the transformer pipeline."""
    mock = Mock()
    mock.return_value = [{"label": "neutral", "score": 0.9}]
    return mock

def test_map_emotion_to_tone():
    """Test mapping of transformer emotions to tone."""
    assert map_emotion_to_tone("joy") == "casual"
    assert map_emotion_to_tone("happiness") == "casual"
    assert map_emotion_to_tone("neutral") == "formal"
    assert map_emotion_to_tone("anger") == "formal"
    assert map_emotion_to_tone("unknown") == "formal"  # Unrecognized emotion
    assert map_emotion_to_tone("  JOY  ") == "casual"  # Case and whitespace handling

def test_detect_tone_with_transformer(mock_classifier):
    """Test tone detection using transformer model."""
    with patch("app.core.classifier.init_tone_classifier", return_value=mock_classifier):
        # Neutral → formal
        mock_classifier.return_value = [{"label": "neutral", "score": 0.9}]
        assert detect_tone("Please provide the ROI table.", clf=mock_classifier) == "formal"
        
        # Joy → casual
        mock_classifier.return_value = [{"label": "joy", "score": 0.8}]
        assert detect_tone("Great to hear from you!", clf=mock_classifier) == "casual"

def test_detect_tone_transformer_failure():
    """Test tone detection when transformer fails, falling back to heuristic."""
    with patch("app.core.classifier.init_tone_classifier", return_value=None):
        # Fallback: exclamation rate > 2%
        assert detect_tone("Wow!!!") == "casual"
        # Fallback: emojis ≥ 2
        assert detect_tone("Let's meet! 😊😉") == "casual"
        # Fallback: casual keywords
        assert detect_tone("Yo, what's up?") == "casual"
        # Fallback: formal
        assert detect_tone("Please provide the ROI table.") == "formal"

def test_detect_tone_empty_input():
    """Test tone detection with empty or whitespace input."""
    assert detect_tone("") == "formal"
    assert detect_tone("   ") == "formal"

def test_detect_tone_long_text(mock_classifier):
    """Test tone detection with long text requiring truncation."""
    long_text = "Please provide the ROI table. " * 200  # >512 words
    with patch("app.core.classifier.init_tone_classifier", return_value=mock_classifier):
        mock_classifier.return_value = [{"label": "neutral", "score": 0.9}]
        assert detect_tone(long_text, clf=mock_classifier) == "formal"

def test_detect_tone_emoji_edge_cases():
    """Test tone detection with edge-case emoji scenarios in fallback."""
    # Exactly 2 emojis
    assert detect_tone("Hi 😊😉") == "casual"
    # 1 emoji (not enough)
    assert detect_tone("Hi 😊") == "formal"
    # Mixed emoji and text
    assert detect_tone("Meeting soon? 😊😉 Thanks!") == "casual"

def test_detect_tone_exclamation_edge_cases():
    """Test tone detection with edge-case exclamation rates in fallback."""
    # Exclamation rate > 2%
    text = "Hi!" * 10  # 10 chars, 10 exclamations → 100%
    assert detect_tone(text) == "casual"
    # Exclamation rate ≤ 2%
    text = "Hi there. This is a long formal message."  # No exclamations
    assert detect_tone(text) == "formal"

def test_detect_tone_transformer_failure():
    """Test tone detection when transformer fails, falling back to heuristic."""
    with patch("app.core.classifier.init_tone_classifier", return_value=None):
        assert detect_tone("Wow!!!", clf=None) == "casual"
        assert detect_tone("Let's meet! 😊😉", clf=None) == "casual"
        assert detect_tone("Yo, what's up?", clf=None) == "casual"
        assert detect_tone("Please provide the ROI table.", clf=None) == "formal"
        assert detect_tone("Hi there! This is a test.", clf=None) == "casual"

def test_detect_tone_empty_input():
    """Test tone detection with empty or whitespace input."""
    assert detect_tone("", clf=None) == "formal"
    assert detect_tone("   ", clf=None) == "formal"
    
def test_detect_tone_casual_keywords():
    """Test tone detection with casual keywords in fallback."""
    assert detect_tone("Hey, let's meet soon!") == "casual"
    assert detect_tone("Cheers, looks good.") == "casual"
    assert detect_tone("Lol, that's awesome!") == "casual"
    assert detect_tone("Dear Sir, please confirm.") == "formal"

def test_init_tone_classifier_failure():
    """Test classifier initialization failure."""
    with patch("app.core.classifier.pipeline", side_effect=Exception("Model load error")):
        assert init_tone_classifier() is None