import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path

class CodeRunner:
    def __init__(self):
        self.supported_languages = {
            "HTML/CSS": "html",
            "Python": "python", 
            "Java": "java",
            "C/C++": "cpp"
        }
        
    def render_code_runner(self):
        """Main method to render the code runner interface"""
        st.subheader("💻 Code Runner IDE")
        
        # Language selection
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_language = st.selectbox(
                "Select Programming Language:",
                list(self.supported_languages.keys()),
                index=0
            )
        with col2:
            if st.button("🔄 Reset Code"):
                self._reset_code(selected_language)
        
        # Route to appropriate IDE
        if selected_language == "HTML/CSS":
            self._render_html_css_ide()
        elif selected_language == "Python":
            self._render_coming_soon("Python")
        elif selected_language == "Java":
            self._render_coming_soon("Java")
        elif selected_language == "C/C++":
            self._render_coming_soon("C/C++")
    
    def _render_html_css_ide(self):
        """Render the HTML/CSS IDE interface"""
        st.markdown("#### 🌐 HTML/CSS IDE")
        
        # Initialize session state for HTML/CSS
        if 'html_code' not in st.session_state:
            st.session_state.html_code = self._get_default_html()
        if 'css_code' not in st.session_state:
            st.session_state.css_code = self._get_default_css()
        
        # Layout options
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            layout_mode = st.selectbox(
                "Layout Mode:",
                ["Horizontal Split", "Vertical Split", "Tabs"]
            )
        with col2:
            preview_mode = st.selectbox(
                "Preview Mode:",
                ["Live Preview", "Manual Refresh"]
            )
        with col3:
            if st.button("▶️ Run Code"):
                st.session_state.force_refresh = True
        
        # Code editor layout
        if layout_mode == "Horizontal Split":
            self._render_horizontal_split()
        elif layout_mode == "Vertical Split":
            self._render_vertical_split()
        elif layout_mode == "Tabs":
            self._render_tabs_layout()
        
        # Preview section
        st.markdown("---")
        st.markdown("#### 👁️ Live Preview")
        
        # Generate and display preview
        self._render_preview()
        
        # Download options
        st.markdown("---")
        self._render_download_options()
    
    def _render_horizontal_split(self):
        """Render HTML and CSS editors side by side"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📄 HTML")
            html_code = st.text_area(
                "HTML Code:",
                value=st.session_state.html_code,
                height=400,
                key="html_editor",
                label_visibility="collapsed"
            )
            st.session_state.html_code = html_code
            
        with col2:
            st.markdown("##### 🎨 CSS")
            css_code = st.text_area(
                "CSS Code:",
                value=st.session_state.css_code,
                height=400,
                key="css_editor",
                label_visibility="collapsed"
            )
            st.session_state.css_code = css_code
    
    def _render_vertical_split(self):
        """Render HTML and CSS editors vertically"""
        st.markdown("##### 📄 HTML")
        html_code = st.text_area(
            "HTML Code:",
            value=st.session_state.html_code,
            height=250,
            key="html_editor_v",
            label_visibility="collapsed"
        )
        st.session_state.html_code = html_code
        
        st.markdown("##### 🎨 CSS")
        css_code = st.text_area(
            "CSS Code:",
            value=st.session_state.css_code,
            height=250,
            key="css_editor_v",
            label_visibility="collapsed"
        )
        st.session_state.css_code = css_code
    
    def _render_tabs_layout(self):
        """Render HTML and CSS editors in tabs"""
        tab1, tab2 = st.tabs(["📄 HTML", "🎨 CSS"])
        
        with tab1:
            html_code = st.text_area(
                "HTML Code:",
                value=st.session_state.html_code,
                height=400,
                key="html_editor_tab",
                label_visibility="collapsed"
            )
            st.session_state.html_code = html_code
            
        with tab2:
            css_code = st.text_area(
                "CSS Code:",
                value=st.session_state.css_code,
                height=400,
                key="css_editor_tab",
                label_visibility="collapsed"
            )
            st.session_state.css_code = css_code
    
    def _render_preview(self):
        """Render the HTML/CSS preview"""
        # Combine HTML and CSS
        combined_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Runner Preview</title>
            <style>
                {st.session_state.css_code}
            </style>
        </head>
        <body>
            {st.session_state.html_code}
        </body>
        </html>
        """
        
        # Display preview
        try:
            components.html(combined_html, height=500, scrolling=True)
        except Exception as e:
            st.error(f"Preview Error: {str(e)}")
            st.code(combined_html, language="html")
    
    def _render_download_options(self):
        """Render download options for the code"""
        st.markdown("#### 📥 Download Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download HTML file
            st.download_button(
                "📄 Download HTML",
                st.session_state.html_code,
                file_name="index.html",
                mime="text/html"
            )
        
        with col2:
            # Download CSS file
            st.download_button(
                "🎨 Download CSS",
                st.session_state.css_code,
                file_name="styles.css",
                mime="text/css"
            )
        
        with col3:
            # Download combined HTML file
            combined_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Runner Export</title>
    <style>
        {st.session_state.css_code}
    </style>
</head>
<body>
    {st.session_state.html_code}
</body>
</html>"""
            st.download_button(
                "📦 Download Combined",
                combined_html,
                file_name="complete.html",
                mime="text/html"
            )
    
    def _render_coming_soon(self, language):
        """Render coming soon message for other languages"""
        st.markdown(f"#### 🚧 {language} IDE - Coming Soon!")
        
        st.info(f"""
        The **{language}** IDE is currently under development. 
        
        **Planned Features:**
        - Syntax highlighting
        - Code completion
        - Error detection
        - Code execution
        - Debug console
        - File management
        """)
        
        # Placeholder code editor
        st.markdown(f"##### Code Editor Preview ({language})")
        placeholder_code = self._get_placeholder_code(language)
        st.code(placeholder_code, language=language.lower())
        
        st.warning("This is a preview. Full functionality will be available soon!")
    
    def _get_default_html(self):
        """Get default HTML template"""
        return """<div class="container">
    <header>
        <h1>Welcome to Code Runner!</h1>
        <p>Edit the HTML and CSS to see live changes</p>
    </header>
    
    <main>
        <section class="card">
            <h2>Getting Started</h2>
            <p>This is a simple HTML/CSS IDE. You can:</p>
            <ul>
                <li>Edit HTML in the left panel</li>
                <li>Edit CSS in the right panel</li>
                <li>See live preview below</li>
                <li>Download your code</li>
            </ul>
        </section>
        
        <section class="card">
            <h2>Features</h2>
            <div class="feature-grid">
                <div class="feature">
                    <h3>📝 Live Editing</h3>
                    <p>See changes instantly</p>
                </div>
                <div class="feature">
                    <h3>💾 Export Options</h3>
                    <p>Download HTML, CSS, or combined</p>
                </div>
                <div class="feature">
                    <h3>🎨 Flexible Layout</h3>
                    <p>Choose your preferred layout</p>
                </div>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2025 Code Runner IDE</p>
    </footer>
</div>"""
    
    def _get_default_css(self):
        """Get default CSS template"""
        return """/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

/* Header Styles */
header {
    text-align: center;
    margin-bottom: 3rem;
    color: white;
}

header h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

/* Main Content */
main {
    display: grid;
    gap: 2rem;
    margin-bottom: 3rem;
}

.card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
}

.card h2 {
    color: #2c3e50;
    margin-bottom: 1rem;
    font-size: 1.8rem;
}

.card p {
    margin-bottom: 1rem;
    color: #555;
}

.card ul {
    margin-left: 2rem;
    margin-bottom: 1rem;
}

.card li {
    margin-bottom: 0.5rem;
    color: #666;
}

/* Feature Grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}

.feature {
    background: rgba(103, 126, 234, 0.1);
    padding: 1.5rem;
    border-radius: 10px;
    text-align: center;
    border: 1px solid rgba(103, 126, 234, 0.2);
}

.feature h3 {
    color: #667eea;
    margin-bottom: 1rem;
    font-size: 1.2rem;
}

.feature p {
    color: #666;
    font-size: 0.9rem;
}

/* Footer */
footer {
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
    padding: 2rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}

/* Responsive Design */
@media (max-width: 768px) {
    .container {
        padding: 1rem;
    }
    
    header h1 {
        font-size: 2rem;
    }
    
    .feature-grid {
        grid-template-columns: 1fr;
    }
}

/* Animations */
.card {
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.feature:hover {
    transform: translateY(-5px);
    transition: transform 0.3s ease;
}"""
    
    def _get_placeholder_code(self, language):
        """Get placeholder code for different languages"""
        placeholders = {
            "Python": '''# Python Code Runner (Coming Soon)
def hello_world():
    print("Hello from Python!")
    
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
if __name__ == "__main__":
    hello_world()
    
    # Calculate first 10 Fibonacci numbers
    print("Fibonacci sequence:")
    for i in range(10):
        print(f"F({i}) = {fibonacci(i)}")''',
        
            "Java": '''// Java Code Runner (Coming Soon)
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        
        // Example: Calculate factorial
        int number = 5;
        long factorial = calculateFactorial(number);
        System.out.println("Factorial of " + number + " is: " + factorial);
    }
    
    public static long calculateFactorial(int n) {
        if (n <= 1) {
            return 1;
        }
        return n * calculateFactorial(n - 1);
    }
}''',
        
            "C/C++": '''// C++ Code Runner (Coming Soon)
#include <iostream>
#include <vector>
using namespace std;

int main() {
    cout << "Hello from C++!" << endl;
    
    // Example: Array operations
    vector<int> numbers = {1, 2, 3, 4, 5};
    
    cout << "Array elements: ";
    for (int num : numbers) {
        cout << num << " ";
    }
    cout << endl;
    
    // Calculate sum
    int sum = 0;
    for (int num : numbers) {
        sum += num;
    }
    cout << "Sum: " << sum << endl;
    
    return 0;
}'''
        }
        
        return placeholders.get(language, "// Code example coming soon...")
    
    def _reset_code(self, language):
        """Reset code to default templates"""
        if language == "HTML/CSS":
            st.session_state.html_code = self._get_default_html()
            st.session_state.css_code = self._get_default_css()
            st.success("HTML/CSS code reset to default template!")
        else:
            st.info(f"{language} reset will be available when the IDE is implemented.")

# Factory function to create and return the code runner instance
def create_code_runner():
    """Factory function to create a CodeRunner instance"""
    return CodeRunner()