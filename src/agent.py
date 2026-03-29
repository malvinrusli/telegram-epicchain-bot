import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/agent_system_prompt.txt")
    with open(prompt_path, "r") as f:
        return f.read()

BRAND_VOICE_PROMPT = load_prompt()

class EpicAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def process_message(self, username, message, context):
        prompt = f"{BRAND_VOICE_PROMPT}\n\nUSER: {username}\nMESSAGE: {message}\n\nCONTEXT FROM KB:\n{context}\n\nRESPONSE:"
        
        response = self.model.generate_content(prompt)
        text = response.text.strip()
        
        if "[IGNORE]" in text:
            return None
            
        # Strip any existing tags the LLM might have hallucinated (e.g. @[username] or @username)
        import re
        text = re.sub(r'|'.join([r'@\[' + re.escape(username) + r'\]', r'@' + re.escape(username)]), '', text).strip()
        # Also strip generic @[username] placeholder if it appears
        text = re.sub(r'@\[username\]', '', text).strip()
            
        # Ensure tagging is handled correctly and avoid double tags
        user_tag = f"@{username}"
        return f"{user_tag} {text}"

if __name__ == "__main__":
    # Test
    agent = EpicAgent()
    print("Testing 'What is the max supply?'")
    print(agent.process_message("JohnDoe", "What is the max supply?", "## The circ, total, and max supply is 33,600,000 EPIC."))
    print("\nTesting 'Nice logo'")
    print(agent.process_message("JohnDoe", "Nice logo", "## Logo Symbology: 'E' with a wing motif."))
