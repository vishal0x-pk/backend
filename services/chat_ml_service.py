import google.generativeai as genai
import os

class ChatMLModel:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.is_trained = True # For compatibility with existing flow
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

        # Robust System Prompt for Kisan Sahayak
        self.system_prompt = (
            "You are 'Kisan Sahayak', a helpful AI Assistant for a Farm Loan Platform. "
            "Your goal is to help farmers with loan applications, status, crop advice, and KYC.\n\n"
            "CORE RULES:\n"
            "1. Use simple, farmer-friendly language (Hindi-mixed English/Hinglish is encouraged).\n"
            "2. Keep responses short (2-6 lines max).\n"
            "3. Use bullet points for steps or lists.\n"
            "4. NEVER fail due to grammar or typos; infer intent from Hinglish words.\n"
            "5. If exact intent is unclear, pick the most likely one and ask ONE short clarification question.\n"
            "6. Knowledge Domains: Platform workflows, Loan approval logic, Agriculture seasons (Rabi/Kharif), Govt. schemes, Verification steps.\n\n"
            "EXAMPLES:\n"
            "- User: 'seed kab sasta milega' -> Talk about Govt. subsidies and seed timing.\n"
            "- User: 'loan reject kyu hua' -> Explain risk factors like low land size or income.\n"
            "- User: 'stutus kya hai' -> Guide them to the Dashboard Timeline."
        )

    def train(self):
        # No training needed for LLM, just a stub for compatibility
        pass

    def predict(self, message):
        if not self.api_key:
            return (
                "⚠️ **Gemini API Key missing.** \n\n"
                "I am ready to help, but my brain needs a configuration update! \n"
                "Please add `GEMINI_API_KEY` to the environment variables."
            )
        
        try:
            # Combine system prompt with user message for stateless chat
            # Using generate_content for simplicity in this integration
            response = self.model.generate_content(
                f"{self.system_prompt}\n\nUser Question: {message}\nKisan Sahayak AI:"
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I am having a bit of trouble thinking right now. 🙏 Please try asking again in a moment or call our helpline: 8317300932."

# Singleton instance
model = ChatMLModel()

