import streamlit as st
import pandas as pd
from streamlit_drawable_canvas import st_canvas
import json
from PIL import Image
import io
import base64

from tools.text_rich_mark import create_text_editor
from tools.ocr_itt import create_ocr_tool
from tools.code_runner import create_code_runner
from tools.ai_tools import create_ai_tools
from tools.file_conversion import create_file_converter

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dev Link - Your AI Productivity Hub",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --- 2. STATE MANAGEMENT ---
# Initialize session state for the active tool
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = None
if 'spreadsheet_data' not in st.session_state:
    st.session_state.spreadsheet_data = pd.DataFrame({
        'Task': ['Initial Setup', 'Add Features'],
        'Status': ['Done', 'In Progress'],
        'Priority': ['High', 'Medium']
    })

# Function to toggle the main tool display
def set_active_tool(tool_name):
    if st.session_state.active_tool == tool_name:
        st.session_state.active_tool = None  # Hide if same button is clicked
    else:
        st.session_state.active_tool = tool_name

# --- 3. ENHANCED STYLING (CSS) ---
st.markdown("""
<style>
/* --- Import Google Fonts --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* --- General & Fonts --- */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* --- Hide Streamlit Menu --- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* --- Main Container --- */
.main > div {
    padding-top: 2rem;
}

/* --- Background Gradient --- */
.stApp {
    background: linear-gradient(135deg, #FFFFFF 0%, #764ba2 100%);
    min-height: 100vh;
}

/* --- Main Title --- */
.main-title {
    font-size: 4rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 2rem;
    color: #ffffff;
    text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    letter-spacing: -2px;
    animation: fadeInUp 0.8s ease-out;
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

/* --- Button Styling --- */
.stButton>button {
    width: 100%;
    height: 50px;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 500;
    border: none;
    background: rgba(255, 255, 255, 0.95);
    color: #2d3748;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.4);
}

.stButton>button:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 1);
    color: #1a202c;
    border: 1px solid rgba(255, 255, 255, 0.6);
}



.stButton>button:active {
    transform: translateY(-1px) scale(1.01);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

/* --- Tool Container Styling --- */
.tool-container {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(20px);
    animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* --- Sidebar Styling --- */
.css-1d391kg {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.3);
}

/* --- Info Box Styling --- */
.stInfo {
    background: rgba(52, 152, 219, 0.1);
    border: 1px solid rgba(52, 152, 219, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* --- Warning Box Styling --- */
.stWarning {
    background: rgba(255, 193, 7, 0.1);
    border: 1px solid rgba(255, 193, 7, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

/* --- Subheader Styling --- */
.stSubheader {
    color: #2d3748;
    font-weight: 600;
    margin-bottom: 1.5rem;
    font-size: 1.5rem;
}

/* --- Drawing Controls --- */
.drawing-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: rgba(248, 249, 250, 0.8);
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

/* --- Separator --- */
.separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.2);
    margin: 1.5rem 0;
    border: none;
}

/* --- Floating Elements --- */
.floating-element {
    position: relative;
    z-index: 10;
}

/* --- Custom Select Styling --- */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 8px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

/* --- Text Area Styling --- */
.stTextArea > div > div > textarea {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.1);
    font-family: 'Inter', sans-serif;
}

/* --- Data Editor Styling --- */
.stDataEditor {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
            div[data-testid="stVerticalBlock"] > div > div:empty {
    height: 0px !important;
    min-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
    border: none !important;
    background: transparent !important;
}

/* Target specific Streamlit div structures that might appear as separators */
div[data-testid="stHorizontalBlock"] + div[data-testid="stVerticalBlock"] > div > div:empty {
    height: 0px !important;
    min-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
    border: none !important;
    background: transparent !important;
}

/* More general approach for divs that might act as separators */
div[data-testid^="st"] > div:empty { /* Targets empty divs directly under Streamlit components */
    height: 0px !important;
    min-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
    border: none !important;
    background: transparent !important;
}

/* Ensure no default borders or backgrounds on column containers */
.st-emotion-cache-1kyxreqf { /* This is a common Streamlit column div class, inspect your app for exact class */
    border: none !important;
    background: transparent !important;
}

</style>
""", unsafe_allow_html=True)

link_url = "https://jaiho-labs.onrender.com" 

# --- 4. ENHANCED SIDEBAR ---
with st.sidebar:
    st.markdown("### 👤 Profile")
    st.info("User Authentication coming soon!")
    
    st.markdown("---")
    st.markdown("### 🛠️ Utilities")
    
    utilities = {
        "📚 Prompt Library": "Prompt Library",
        "📦 GitHub Integration": "GitHub Integration",
        "⚙️ Regex Tester": "Regex Tester",
        "🗜️ File Compressor": "File Compressor",
        "🌐 Translator": "Translator"
    }
    
    for btn_text, tool_name in utilities.items():
        if st.button(btn_text, key=f"util_{tool_name}"):
            set_active_tool(tool_name)
    
    st.markdown("---")
    st.markdown("### 📊 Stats")
    st.metric("Tools Available", "15")
    st.metric("Active Sessions", "1")
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("**Dev Link** © 2025\n\nYour AI productivity hub for development and creative work.")
    st.markdown("---")
    #st.markdown("#### Developed by Jaiho Labs",unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size: 1.3rem; text-align: center;">
            Developed by 
            <a 
                href="{link}" 
                target="_blank" 
                style="text-decoration: none;"
            >
                <span style="
                    background-image: linear-gradient(to right, #6A82FB, #FC5C7D);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: bold;
                ">
                    Jaiho Labs
                </span>
                <span style="
                    color: #FC5C7D; /* Matches the end color of the gradient */
                    font-size: 1.2rem;
                ">
                    ↗
                </span>
            </a>
        </div>
        """.format(link=link_url),
        unsafe_allow_html=True
    )



# --- 5. HEADER AND MAIN NAVIGATION ---
st.markdown('<h2 class="main-title">🖥️ Dev Link</h2>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: rgba(255, 255, 255, 0.8); font-size: 1.3rem; margin-bottom: 2rem;">Your AI Productivity Hub</p>', unsafe_allow_html=True)

# --- Row 1 of Buttons ---
st.markdown("### General Purpose Tools")
cols1 = st.columns(5)
buttons1 = {
    "📝 Notepad": "Notepad",
    "📊 Spreadsheet": "Spreadsheet", 
    "🎨 Drawing Tool": "Drawing Tool",
    "🔄 File Converter": "File Converter",
    "📸 OCR": "OCR"
}
for i, (btn_text, tool_name) in enumerate(buttons1.items()):
    if cols1[i].button(btn_text, key=f"main_{tool_name}"):
        set_active_tool(tool_name)

# --- Row 2 of Buttons ---
st.markdown("### AI Developer Tools")
cols2 = st.columns(5)
buttons2 = {
    "💻 Code Runner": "Code Runner",
    "🛠️ AI Tools": "AI Tools",
    "🎙️ Smart Note": "Smart Note",
    "🧠 Mind Map": "Mind Map Generator",
    "💡 Brainstorm": "Brainstorming Board"
}
for i, (btn_text, tool_name) in enumerate(buttons2.items()):
    if cols2[i].button(btn_text, key=f"adv_{tool_name}"):
        set_active_tool(tool_name)


# --- 6. DYNAMIC TOOL DISPLAY AREA ---
if st.session_state.active_tool:
    # Moved the separator here so it appears only when a tool is active
    st.markdown('<hr class="separator">', unsafe_allow_html=True) 
    with st.container():
        st.markdown('<div class="tool-container">', unsafe_allow_html=True)
        
        active_tool = st.session_state.active_tool
        
        if active_tool == "Notepad":
            text_editor = create_text_editor()
            text_editor.render_notepad()

        elif active_tool == "Spreadsheet":
            st.subheader("📊 Smart Spreadsheet")
            
            # Spreadsheet controls
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if st.button("➕ Add Column"):
                    new_col_name = f"Column_{len(st.session_state.spreadsheet_data.columns) + 1}"
                    st.session_state.spreadsheet_data[new_col_name] = ""
            with col2:
                if st.button("🗑️ Reset Data"):
                    st.session_state.spreadsheet_data = pd.DataFrame({
                        'Task': ['Initial Setup'],
                        'Status': ['Done'],
                        'Priority': ['High']
                    })
            with col3:
                num_rows = st.number_input("Rows", min_value=1, value=len(st.session_state.spreadsheet_data), max_value=100)
            
            # Data editor
            edited_df = st.data_editor(
                st.session_state.spreadsheet_data,
                num_rows="dynamic",
                use_container_width=True,
                height=400,
                key="spreadsheet_editor"
            )
            
            # Update session state
            st.session_state.spreadsheet_data = edited_df
            
            # Download options
            col1, col2 = st.columns(2)
            with col1:
                csv_data = edited_df.to_csv(index=False)
                st.download_button("⬇️ Download as CSV", csv_data, "spreadsheet.csv", "text/csv")
            with col2:
                json_data = edited_df.to_json(orient='records', indent=2)
                st.download_button("⬇️ Download as JSON", json_data, "spreadsheet.json", "application/json")

        elif active_tool == "Drawing Tool":
            st.subheader("🎨 Advanced Drawing Tool")
            
            # Drawing controls
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                drawing_mode = st.selectbox(
                    "Mode", 
                    ["freedraw", "line", "rect", "circle", "polygon", "transform"],
                    index=0
                )
            
            with col2:
                stroke_width = st.slider("Brush Size", 1, 50, 5)
            
            with col3:
                stroke_color = st.color_picker("Color", "#000000")
            
            with col4:
                fill_color = st.color_picker("Fill Color", "#ffffff")
            
            with col5:
                if st.button("🗑️ Clear Canvas"):
                    st.rerun()
            
            # Additional controls
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                canvas_width = st.slider("Canvas Width", 400, 1200, 800)
            with col2:
                canvas_height = st.slider("Canvas Height", 300, 800, 600)
            with col3:
                background_color = st.color_picker("Background", "#ffffff")
            
            # Canvas
            canvas_result = st_canvas(
                fill_color=fill_color,
                stroke_width=stroke_width,
                stroke_color=stroke_color,
                background_color=background_color,
                width=canvas_width,
                height=canvas_height,
                drawing_mode=drawing_mode,
                key="advanced_canvas",
                display_toolbar=True
            )
            
            # Save options
            if canvas_result.image_data is not None:
                col1, col2 = st.columns(2)
                with col1:
                    # Convert to PIL Image and save
                    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format='PNG')
                    st.download_button(
                        "⬇️ Download as PNG",
                        img_buffer.getvalue(),
                        "drawing.png",
                        "image/png"
                    )
                with col2:
                    # Save as JSON
                    if canvas_result.json_data:
                        json_data = json.dumps(canvas_result.json_data, indent=2)
                        st.download_button(
                            "⬇️ Download as JSON",
                            json_data,
                            "drawing.json",
                            "application/json"
                        )

        elif active_tool == "File Converter":
            file_convert = create_file_converter()
            file_convert.render_file_converter()

        elif active_tool == "OCR":
            ocr_tool = create_ocr_tool()
            ocr_tool.render_ocr_tool()

        elif active_tool == "Code Runner":
            code_runner = create_code_runner()
            code_runner.render_code_runner()

        elif active_tool == "AI Tools":
            ai_tool = create_ai_tools()
            ai_tool.render_ai_tools()
            

        elif active_tool == "Brainstorming Board":
            st.subheader("💡 AI-Powered Brainstorming")
            
            # Brainstorming input
            topic = st.text_input("Enter a topic or challenge:", placeholder="e.g., 'New mobile app features'")
            
            col1, col2 = st.columns(2)
            with col1:
                brainstorm_type = st.selectbox("Brainstorming Type", ["Ideas", "Solutions", "Features", "Improvements"])
            with col2:
                num_ideas = st.slider("Number of Ideas", 5, 20, 10)
            
            if topic and st.button("💡 Generate Ideas"):
                st.info("AI brainstorming feature will be implemented soon!")
                
            # Manual idea board
            st.markdown("#### Manual Idea Board")
            if 'ideas' not in st.session_state:
                st.session_state.ideas = []
            
            new_idea = st.text_input("Add your own idea:")
            if st.button("➕ Add Idea") and new_idea:
                st.session_state.ideas.append(new_idea)
                st.success(f"Added: {new_idea}")
            
            # Display ideas
            if st.session_state.ideas:
                st.markdown("##### Your Ideas:")
                for i, idea in enumerate(st.session_state.ideas):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.write(f"💡 {idea}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{i}"):
                            st.session_state.ideas.pop(i)
                            st.rerun()

        # Add placeholders for other tools
        else:
            st.subheader(f"🛠️ {active_tool}")
            st.warning(f"The **{active_tool}** tool is currently under development.")
            st.markdown(f"""
            ### Coming Soon Features:
            - Enhanced functionality for {active_tool}
            - AI-powered assistance
            - Export and sharing options
            - Integration with other tools
            """)

        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem; background: rgba(255, 255, 255, 0.1); border-radius: 24px; margin-top: 2rem; backdrop-filter: blur(20px);">
        <h2 style="color: white; margin-bottom: 1rem;">Welcome to Dev Link! 🚀</h2>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.1rem; margin-bottom: 2rem;">
            Select any tool from the navigation above to begin your productivity journey.
        </p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 12px; min-width: 200px;">
                <h4 style="color: white; margin-bottom: 0.5rem;">General Purpose Tools</h4>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Essential productivity tools for daily work</p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 12px; min-width: 200px;">
                <h4 style="color: white; margin-bottom: 0.5rem;">AI Developer Tools</h4>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">AI-powered tools for enhanced productivity</p>
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 1rem; border-radius: 12px; min-width: 200px;">
                <h4 style="color: white; margin-bottom: 0.5rem;">Utilities</h4>
                <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">Additional tools and integrations</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    