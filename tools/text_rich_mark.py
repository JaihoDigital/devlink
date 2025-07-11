import streamlit as st
import streamlit.components.v1 as components
import markdown
import re
from datetime import datetime

class TextEditor:
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables for the text editor"""
        if 'editor_content' not in st.session_state:
            st.session_state.editor_content = ""
        if 'editor_format' not in st.session_state:
            st.session_state.editor_format = "Plain Text"
        if 'show_preview' not in st.session_state:
            st.session_state.show_preview = False
    
    def render_notepad(self):
        """Main function to render the notepad interface"""
        st.subheader("📝 Smart Notepad")
        
        # Format selection and options
        self.render_format_controls()
        
        # Editor area based on selected format
        if st.session_state.editor_format == "Plain Text":
            self.render_plain_text_editor()
        elif st.session_state.editor_format == "Markdown":
            self.render_markdown_editor()
        elif st.session_state.editor_format == "Rich Text":
            self.render_rich_text_editor()
        
        # Common controls
        self.render_common_controls()
    
    def render_format_controls(self):
        """Render format selection and common controls"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            format_options = ["Plain Text", "Markdown", "Rich Text"]
            st.session_state.editor_format = st.selectbox(
                "Format", 
                format_options, 
                index=format_options.index(st.session_state.editor_format)
            )
        
        with col2:
            if st.session_state.editor_format == "Markdown":
                st.session_state.show_preview = st.checkbox("Show Preview", value=st.session_state.show_preview)
            else:
                st.session_state.show_preview = False
        
        with col3:
            word_count = st.checkbox("Show Word Count", value=True)
        
        return word_count
    
    def render_plain_text_editor(self):
        """Render plain text editor"""
        st.session_state.editor_content = st.text_area(
            "Write your notes here...",
            value=st.session_state.editor_content,
            height=400,
            placeholder="Start typing your notes...",
            label_visibility="collapsed"
        )
    
    def render_markdown_editor(self):
        """Render markdown editor with preview"""
        if st.session_state.show_preview:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Editor**")
                st.session_state.editor_content = st.text_area(
                    "Markdown Editor",
                    value=st.session_state.editor_content,
                    height=350,
                    placeholder=self.get_markdown_placeholder(),
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown("**Preview**")
                if st.session_state.editor_content:
                    try:
                        # Convert markdown to HTML
                        html_content = markdown.markdown(
                            st.session_state.editor_content,
                            extensions=['fenced_code', 'tables', 'toc']
                        )
                        st.markdown(html_content, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Preview error: {str(e)}")
                else:
                    st.info("Preview will appear here as you type...")
        else:
            st.session_state.editor_content = st.text_area(
                "Markdown Editor",
                value=st.session_state.editor_content,
                height=400,
                placeholder=self.get_markdown_placeholder(),
                label_visibility="collapsed"
            )
        
        # Markdown toolbar
        self.render_markdown_toolbar()
    
    def render_rich_text_editor(self):
        """Render rich text editor with formatting options"""
        # Rich text toolbar
        self.render_rich_text_toolbar()
        
        # Rich text editor using HTML component
        self.render_rich_text_component()
    
    def render_markdown_toolbar(self):
        """Render markdown formatting toolbar"""
        st.markdown("**Markdown Toolbar**")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            if st.button("**Bold**", help="Add bold text"):
                self.insert_markdown_format("**", "**", "bold text")
        
        with col2:
            if st.button("*Italic*", help="Add italic text"):
                self.insert_markdown_format("*", "*", "italic text")
        
        with col3:
            if st.button("# Header", help="Add header"):
                self.insert_markdown_format("# ", "", "Header")
        
        with col4:
            if st.button("- List", help="Add bullet point"):
                self.insert_markdown_format("- ", "", "List item")
        
        with col5:
            if st.button("```Code```", help="Add code block"):
                self.insert_markdown_format("```\n", "\n```", "code here")
        
        with col6:
            if st.button("[Link]", help="Add link"):
                self.insert_markdown_format("[", "](url)", "link text")
    
    def render_rich_text_toolbar(self):
        """Render rich text formatting toolbar"""
        st.markdown("**Rich Text Toolbar**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            font_size = st.selectbox("Font Size", ["12px", "14px", "16px", "18px", "20px", "24px"], index=2)
        
        with col2:
            text_color = st.color_picker("Text Color", "#000000")
        
        with col3:
            bg_color = st.color_picker("Background", "#ffffff")
        
        with col4:
            if st.button("**B**", help="Bold"):
                self.apply_rich_text_format("bold")
        
        with col5:
            if st.button("*I*", help="Italic"):
                self.apply_rich_text_format("italic")
        
        # Additional formatting options
        col6, col7, col8, col9, col10 = st.columns(5)
        
        with col6:
            if st.button("U", help="Underline"):
                self.apply_rich_text_format("underline")
        
        with col7:
            if st.button("≡", help="Align Left"):
                self.apply_rich_text_format("alignLeft")
        
        with col8:
            if st.button("≡", help="Align Center"):
                self.apply_rich_text_format("alignCenter")
        
        with col9:
            if st.button("• List", help="Bullet List"):
                self.apply_rich_text_format("bulletList")
        
        with col10:
            if st.button("1. List", help="Number List"):
                self.apply_rich_text_format("numberList")
    
    def render_rich_text_component(self):
        """Render rich text editor using HTML component"""
        rich_text_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .editor {{
                    border: 1px solid #ccc;
                    border-radius: 8px;
                    padding: 10px;
                    min-height: 400px;
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.5;
                }}
                .toolbar {{
                    border: 1px solid #ccc;
                    border-bottom: none;
                    padding: 10px;
                    background: #f5f5f5;
                    border-radius: 8px 8px 0 0;
                }}
                .toolbar button {{
                    margin: 0 5px;
                    padding: 5px 10px;
                    border: 1px solid #ccc;
                    background: white;
                    cursor: pointer;
                    border-radius: 4px;
                }}
                .toolbar button:hover {{
                    background: #e0e0e0;
                }}
            </style>
        </head>
        <body>
            <div class="toolbar">
                <button onclick="document.execCommand('bold')"><b>B</b></button>
                <button onclick="document.execCommand('italic')"><i>I</i></button>
                <button onclick="document.execCommand('underline')"><u>U</u></button>
                <button onclick="document.execCommand('justifyLeft')">←</button>
                <button onclick="document.execCommand('justifyCenter')">↔</button>
                <button onclick="document.execCommand('justifyRight')">→</button>
                <button onclick="document.execCommand('insertUnorderedList')">• List</button>
                <button onclick="document.execCommand('insertOrderedList')">1. List</button>
                <select onchange="document.execCommand('fontSize', false, this.value)">
                    <option value="1">Small</option>
                    <option value="3" selected>Normal</option>
                    <option value="5">Large</option>
                    <option value="7">Huge</option>
                </select>
                <input type="color" onchange="document.execCommand('foreColor', false, this.value)">
            </div>
            <div class="editor" contenteditable="true" id="richEditor" onkeyup="updateContent()">
                {st.session_state.editor_content}
            </div>
            
            <script>
                function updateContent() {{
                    const content = document.getElementById('richEditor').innerHTML;
                    window.parent.postMessage({{
                        type: 'rich_text_update',
                        content: content
                    }}, '*');
                }}
                
                // Listen for messages from parent
                window.addEventListener('message', function(event) {{
                    if (event.data.type === 'rich_text_command') {{
                        document.execCommand(event.data.command, false, event.data.value);
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        components.html(rich_text_html, height=500)
    
    def render_common_controls(self):
        """Render common controls like word count and download options"""
        # Word count display
        if st.session_state.editor_content:
            text_content = self.strip_html_tags(st.session_state.editor_content)
            words = len(text_content.split()) if text_content else 0
            chars = len(text_content)
            st.caption(f"📊 {words} words, {chars} characters")
        
        # Download options
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⬇️ Download as .txt"):
                self.download_file("txt")
        
        with col2:
            if st.button("⬇️ Download as .md"):
                self.download_file("md")
        
        with col3:
            if st.button("⬇️ Download as .html"):
                self.download_file("html")
        
        with col4:
            if st.button("🔄 Clear All"):
                st.session_state.editor_content = ""
                st.rerun()
    
    def insert_markdown_format(self, prefix, suffix, placeholder):
        """Insert markdown formatting at cursor position"""
        current_content = st.session_state.editor_content
        # For now, just append the formatted text
        formatted_text = f"{prefix}{placeholder}{suffix}"
        st.session_state.editor_content = current_content + formatted_text
        st.rerun()
    
    def apply_rich_text_format(self, format_type):
        """Apply rich text formatting"""
        # This would interact with the rich text editor component
        # For now, we'll show a message
        st.info(f"Applied {format_type} formatting")
    
    def get_markdown_placeholder(self):
        """Get markdown placeholder text"""
        return """# Welcome to Markdown Editor

## Features
- **Bold** and *italic* text
- Lists and links
- Code blocks
- Tables
- And much more!

### Example Code Block
```python
def hello_world():
    print("Hello, World!")
```

### Example Table
| Feature | Status |
|---------|--------|
| Bold    | ✅     |
| Italic  | ✅     |
| Lists   | ✅     |

[Learn more about Markdown](https://www.markdownguide.org)
"""
    
    def strip_html_tags(self, text):
        """Remove HTML tags from text for word counting"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def download_file(self, format_type):
        """Handle file downloads"""
        content = st.session_state.editor_content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "txt":
            clean_content = self.strip_html_tags(content)
            st.download_button(
                label="Download TXT",
                data=clean_content,
                file_name=f"note_{timestamp}.txt",
                mime="text/plain",
                key="download_txt"
            )
        
        elif format_type == "md":
            st.download_button(
                label="Download Markdown",
                data=content,
                file_name=f"note_{timestamp}.md",
                mime="text/markdown",
                key="download_md"
            )
        
        elif format_type == "html":
            if st.session_state.editor_format == "Markdown":
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'toc'])
            else:
                html_content = content
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Note</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
                    pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            st.download_button(
                label="Download HTML",
                data=full_html,
                file_name=f"note_{timestamp}.html",
                mime="text/html",
                key="download_html"
            )

# Function to create and return the text editor instance
def create_text_editor():
    """Create and return a text editor instance"""
    return TextEditor()