import os
from openai import OpenAI
import language_tool_python

tool = language_tool_python.LanguageTool("no")

test_message = "Eg liker å spiser epler og du gå til butikken i går."

matches = tool.check(test_message)

for match in matches:
    print(f"Issues: {match.message}")
    print(f"Context: {match.context}")
    print(f"Suggested correction: {match.replacements}")

corrected_text = tool.correct(test_message)
print(f"Corrected Text {corrected_text}")