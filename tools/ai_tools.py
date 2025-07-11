import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

class AITools:
    def __init__(self):
        # OpenRouter provides free access to many models, though an API key is still needed for authentication.
        self.api_key = st.secrets.get("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"

    def make_api_request(self, messages, model, max_tokens):
        """
        Make an API request to OpenRouter using the selected model.
        This function is now more flexible and accepts the model as an argument.
        """
        if not self.api_key:
            st.error("❌ OpenRouter API key not found in secrets.toml")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"❌ API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Connection Error: {str(e)}")
            return None
    
    def render_ai_tools(self):
        """Main AI Tools interface"""
        st.subheader("🤖 AI-Powered Tools")
        
        # Model selection is now limited to free options
        free_models = {
            "Gemma 3 (Free)": "google/gemma-3-27b-it:free",
            "DeepSeek R1 (Free)": "deepseek/deepseek-r1:free",
            "Cypher Alpha (Free) - Code": "openrouter/cypher-alpha:free",
            "Image": "meta-llama/llama-4-maverick:free"
        }
        
        col1, col2 = st.columns([2, 1])
        with col1:
            model_name = st.selectbox(
                "Choose AI Model (All Free on OpenRouter)",
                list(free_models.keys())
            )
            model = free_models[model_name]
        with col2:
            max_tokens = st.slider("Max Tokens", 100, 4000, 1000)
        
        # Tool selection tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Chat", "🔍 Code Explainer", "📄 Doc Summarizer", "🎨 Image Gen", "🔧 Code Gen"
        ])
        
        with tab1:
            # All chat tabs will now use the selected free model
            self.render_chatbot(model, max_tokens)
            
        with tab2:
            self.render_code_explainer(model, max_tokens)
            
        with tab3:
            self.render_document_summarizer(model, max_tokens)
            
        with tab4:
            self.render_image_generator(model, max_tokens)
            
        with tab5:
            self.render_code_generator(model, max_tokens)
    
    def render_chatbot(self, model, max_tokens):
        """Simple chatbot interface"""
        st.markdown("#### 💬 AI Chat Assistant")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask me anything..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    messages = [
                        {"role": "system", "content": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."},
                        *st.session_state.chat_history
                    ]
                    
                    response = self.make_api_request(messages, model, max_tokens)
                    
                    if response and "choices" in response:
                        ai_response = response["choices"][0]["message"]["content"]
                        st.markdown(ai_response)
                        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                    else:
                        st.error("Failed to get response from AI")
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    def render_code_explainer(self, model, max_tokens):
        """Code explanation tool"""
        st.markdown("#### 🔍 Code Explainer")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            code_input = st.text_area(
                "Paste your code here...", 
                height=300,
                placeholder="def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            )
        with col2:
            language = st.selectbox(
                "Programming Language", 
                ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Other"]
            )
            
            explanation_type = st.radio(
                "Explanation Type",
                ["Simple", "Detailed", "Line by Line"]
            )
        
        if st.button("🔍 Explain Code") and code_input:
            with st.spinner("Analyzing code..."):
                prompt = f"""
                Please explain this {language} code. 
                Explanation type: {explanation_type}
                
                Code:
                ```{language.lower()}
                {code_input}
                ```
                
                Please provide a clear explanation of:
                1. What the code does
                2. How it works
                3. Key concepts used
                {"4. Line-by-line breakdown" if explanation_type == "Line by Line" else ""}
                """
                
                messages = [{"role": "user", "content": prompt}]
                response = self.make_api_request(messages, model, max_tokens)
                
                if response and "choices" in response:
                    explanation = response["choices"][0]["message"]["content"]
                    st.markdown("### 📝 Code Explanation")
                    st.markdown(explanation)
                else:
                    st.error("Failed to explain code")
    
    def render_document_summarizer(self, model, max_tokens):
        """Document summarization tool"""
        st.markdown("#### 📄 Document Summarizer")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            document_text = st.text_area(
                "Paste your document text here...", 
                height=300,
                placeholder="Enter the text you want to summarize..."
            )
        with col2:
            summary_length = st.selectbox(
                "Summary Length", 
                ["Brief (1-2 paragraphs)", "Medium (3-4 paragraphs)", "Detailed (5+ paragraphs)"]
            )
            
            summary_style = st.selectbox(
                "Summary Style",
                ["Executive Summary", "Key Points", "Abstract", "Bullet Points"]
            )
        
        uploaded_file = st.file_uploader(
            "Or upload a text file", 
            type=['txt', 'md'],
            help="Upload a .txt or .md file to summarize"
        )
        
        if uploaded_file:
            document_text = str(uploaded_file.read(), "utf-8")
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("📄 Summarize Document") and document_text:
            with st.spinner("Summarizing document..."):
                prompt = f"""
                Please create a {summary_length.split()[0].lower()} summary of the following document in {summary_style.lower()} style:
                
                Document:
                {document_text}
                
                Please provide:
                1. Main themes and topics
                2. Key insights or findings
                3. Important conclusions
                {"4. Present as bullet points" if summary_style == "Bullet Points" else ""}
                """
                
                messages = [{"role": "user", "content": prompt}]
                response = self.make_api_request(messages, model, max_tokens)
                
                if response and "choices" in response:
                    summary = response["choices"][0]["message"]["content"]
                    st.markdown("### 📋 Document Summary")
                    st.markdown(summary)
                    
                    st.download_button(
                        "⬇️ Download Summary",
                        summary,
                        "document_summary.txt",
                        "text/plain"
                    )
                else:
                    st.error("Failed to summarize document")
    
    def render_image_generator(self, model, max_tokens):
        """AI Image Generator (using text-to-image description)"""
        st.markdown("#### 🎨 AI Image Generator")
        
        st.info("🔧 This tool generates detailed image descriptions that can be used with image generation services like DALL-E, Midjourney, or Stable Diffusion.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            image_description = st.text_area(
                "Describe the image you want to generate...",
                height=150,
                placeholder="A futuristic city skyline at sunset with flying cars..."
            )
        with col2:
            image_style = st.selectbox(
                "Art Style",
                ["Photorealistic", "Digital Art", "Oil Painting", "Watercolor", "Sketch", "3D Render", "Anime", "Abstract"]
            )
            
            image_mood = st.selectbox(
                "Mood/Atmosphere",
                ["Bright & Cheerful", "Dark & Moody", "Calm & Peaceful", "Energetic", "Mysterious", "Dramatic"]
            )
        
        if st.button("🎨 Generate Image Prompt") and image_description:
            with st.spinner("Creating detailed image prompt..."):
                prompt = f"""
                Create a detailed, professional image generation prompt based on this description:
                "{image_description}"
                
                Style: {image_style}
                Mood: {image_mood}
                
                Please provide:
                1. An enhanced, detailed prompt optimized for AI image generation
                2. Technical specifications (lighting, composition, camera angle)
                3. Style and quality modifiers
                4. Negative prompts (what to avoid)
                
                Format the response as a ready-to-use prompt for image generation services.
                """
                
                messages = [{"role": "user", "content": prompt}]
                response = self.make_api_request(messages, model, max_tokens)
                
                if response and "choices" in response:
                    image_prompt = response["choices"][0]["message"]["content"]
                    st.markdown("### 🖼️ Generated Image Prompt")
                    st.markdown(image_prompt)
                    
                    st.code(image_prompt, language="text")
                    st.success("✅ Copy the prompt above to use in your favorite image generation tool!")
                else:
                    st.error("Failed to generate image prompt")
    
    def render_code_generator(self, model, max_tokens):
        """AI Code Generator"""
        st.markdown("#### 🔧 Code Generator")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            code_description = st.text_area(
                "Describe what you want to code...",
                height=200,
                placeholder="Create a Python function that calculates the factorial of a number using recursion..."
            )
        with col2:
            programming_language = st.selectbox(
                "Programming Language",
                ["Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "TypeScript"]
            )
            
            code_style = st.selectbox(
                "Code Style",
                ["Clean & Simple", "Well-commented", "Production-ready", "Beginner-friendly"]
            )
            
            include_tests = st.checkbox("Include test cases")
        
        if st.button("🔧 Generate Code") and code_description:
            with st.spinner("Generating code..."):
                prompt = f"""
                Generate {programming_language} code based on this description:
                "{code_description}"
                
                Requirements:
                - Style: {code_style}
                - Language: {programming_language}
                {"- Include comprehensive test cases" if include_tests else ""}
                
                Please provide:
                1. Clean, working code
                2. Clear comments explaining the logic
                3. Usage examples
                {"4. Test cases to verify functionality" if include_tests else ""}
                
                Format the code properly with appropriate syntax highlighting.
                """
                
                messages = [{"role": "user", "content": prompt}]
                response = self.make_api_request(messages, model, max_tokens)
                
                if response and "choices" in response:
                    generated_code = response["choices"][0]["message"]["content"]
                    st.markdown("### 💻 Generated Code")
                    st.markdown(generated_code)
                    
                    file_extension = {
                        "Python": ".py", "JavaScript": ".js", "Java": ".java", 
                        "C++": ".cpp", "C#": ".cs", "Go": ".go", "Rust": ".rs",
                        "PHP": ".php", "Ruby": ".rb", "TypeScript": ".ts"
                    }
                    
                    st.download_button(
                        "⬇️ Download Code",
                        generated_code,
                        f"generated_code{file_extension.get(programming_language, '.txt')}",
                        "text/plain"
                    )
                else:
                    st.error("Failed to generate code")

def create_ai_tools():
    """Factory function to create AI Tools instance"""
    return AITools()