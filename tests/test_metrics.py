from nudger.metrics import classify_tone

def test_formal_tone():
    thread = [{"body": "Please find the updated proposal attached."}]
    assert classify_tone(thread) == "formal"

def test_casual_tone_emojis():
    thread = [{"body": "Hey! Let's go 😄🚀"}]
    assert classify_tone(thread) == "casual"

def test_casual_tone_exclamations():
    thread = [{"body": "Amazing!!!!! Let's make it happen!!!"}]
    assert classify_tone(thread) == "casual"

def test_mixed_thread():
    thread = [
        {"body": "Great job on the numbers!"},
        {"body": "Awesome!! Let's chat soon 😎👍"}
    ]
    assert classify_tone(thread) == "casual"
