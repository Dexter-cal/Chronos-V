from profanity_check import predict

def is_content_safe(text: str) -> bool:
    """
    Checks if a given string contains profanity using the profanity-check model.

    Returns:
        bool: True if the text is safe, False if it contains profanity.
    """
    # The `predict` function returns a list of 0s and 1s.
    # 0 means the text is clean, 1 means it's profane.
    # We are checking a single string, so we get a list with one element.
    prediction = predict([text])

    is_profane = prediction[0] == 1

    # Return the opposite of is_profane
    return not is_profane
