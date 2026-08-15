"""Inline JavaScript for the AI Assistant view."""


def build_js(context):
    return """
var chatHistory = document.getElementById('chat-history');
if (chatHistory) { chatHistory.scrollTop = chatHistory.scrollHeight; }
"""
