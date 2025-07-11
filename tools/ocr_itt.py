import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import io
import base64
from datetime import datetime
import re

class OCRTool:
    def __init__(self):
        self.initialize_session_state()
        self.initialize_ocr_reader()
    
    def initialize_session_state(self):
        """Initialize session state variables for OCR tool"""
        if 'ocr_extracted_text' not in st.session_state:
            st.session_state.ocr_extracted_text = ""
        if 'ocr_confidence_scores' not in st.session_state:
            st.session_state.ocr_confidence_scores = []
        if 'ocr_processing' not in st.session_state:
            st.session_state.ocr_processing = False
        if 'ocr_results_data' not in st.session_state:
            st.session_state.ocr_results_data = []
    
    @st.cache_resource
    def initialize_ocr_reader(_self):
        """Initialize EasyOCR reader with caching"""
        try:
            # Initialize with English model only, no GPU
            reader = easyocr.Reader(['en'], gpu=False)
            return reader
        except Exception as e:
            st.error(f"Failed to initialize OCR reader: {str(e)}")
            return None
    
    def render_ocr_tool(self):
        """Main function to render the OCR interface"""
        st.subheader("📷 OCR - Image to Text Extractor")
        
        # OCR options
        self.render_ocr_options()
        
        # Upload section
        uploaded_file = st.file_uploader(
            "Upload an Image", 
            type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
            help="Supported formats: PNG, JPG, JPEG, BMP, TIFF, WebP"
        )
        
        if uploaded_file:
            self.process_uploaded_image(uploaded_file)
        
        # Results section
        if st.session_state.ocr_extracted_text:
            self.render_results_section()
        
        # Tips section
        self.render_tips_section()
    
    def render_ocr_options(self):
        """Render OCR processing options"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_confidence = st.checkbox("Show Confidence Scores", value=True)
        
        with col2:
            show_bounding_boxes = st.checkbox("Show Bounding Boxes", value=False)
        
        with col3:
            text_processing = st.selectbox(
                "Text Processing",
                ["Raw Text", "Clean Text", "Formatted Text"],
                index=1
            )
        
        return show_confidence, show_bounding_boxes, text_processing
    
    def process_uploaded_image(self, uploaded_file):
        """Process the uploaded image and extract text"""
        try:
            # Display image
            image = Image.open(uploaded_file)
            
            # Image info
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)
            
            with col2:
                st.markdown("**Image Information:**")
                st.write(f"📏 Size: {image.size[0]} × {image.size[1]}")
                st.write(f"📊 Format: {image.format}")
                st.write(f"🎨 Mode: {image.mode}")
                
                # File size
                file_size = len(uploaded_file.getvalue())
                st.write(f"📦 Size: {self.format_file_size(file_size)}")
            
            # Process button
            if st.button("🔍 Extract Text", type="primary"):
                self.extract_text_from_image(image)
        
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
    
    def extract_text_from_image(self, image):
        """Extract text from image using EasyOCR"""
        reader = self.initialize_ocr_reader()
        
        if reader is None:
            st.error("OCR reader not available. Please check your installation.")
            return
        
        try:
            # Show processing message
            with st.spinner("🔄 Processing image... This may take a moment."):
                # Convert PIL image to numpy array
                image_array = np.array(image)
                
                # Run OCR
                results = reader.readtext(image_array)
                
                # Process results
                self.process_ocr_results(results)
                
                st.success("✅ Text extraction completed!")
        
        except Exception as e:
            st.error(f"Error during OCR processing: {str(e)}")
    
    def process_ocr_results(self, results):
        """Process and store OCR results"""
        extracted_texts = []
        confidence_scores = []
        results_data = []
        
        for bbox, text, confidence in results:
            if text.strip():  # Only include non-empty text
                extracted_texts.append(text)
                confidence_scores.append(confidence)
                results_data.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        # Store in session state
        st.session_state.ocr_extracted_text = '\n'.join(extracted_texts)
        st.session_state.ocr_confidence_scores = confidence_scores
        st.session_state.ocr_results_data = results_data
    
    def render_results_section(self):
        """Render the results section with extracted text"""
        st.markdown("---")
        st.subheader("📝 Extracted Text Results")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            word_count = len(st.session_state.ocr_extracted_text.split())
            st.metric("Words", word_count)
        
        with col2:
            char_count = len(st.session_state.ocr_extracted_text)
            st.metric("Characters", char_count)
        
        with col3:
            avg_confidence = np.mean(st.session_state.ocr_confidence_scores) if st.session_state.ocr_confidence_scores else 0
            st.metric("Avg Confidence", f"{avg_confidence:.2f}")
        
        with col4:
            text_blocks = len(st.session_state.ocr_results_data)
            st.metric("Text Blocks", text_blocks)
        
        # Display options
        display_option = st.radio(
            "Display Format:",
            ["Simple Text", "Detailed Results", "Confidence Analysis"],
            horizontal=True
        )
        
        if display_option == "Simple Text":
            self.render_simple_text()
        elif display_option == "Detailed Results":
            self.render_detailed_results()
        elif display_option == "Confidence Analysis":
            self.render_confidence_analysis()
        
        # Download options
        self.render_download_options()
    
    def render_simple_text(self):
        """Render simple extracted text"""
        st.text_area(
            "Extracted Text:",
            value=st.session_state.ocr_extracted_text,
            height=300,
            label_visibility="collapsed"
        )
    
    def render_detailed_results(self):
        """Render detailed results with confidence scores"""
        st.markdown("**Detailed Text Extraction Results:**")
        
        for i, data in enumerate(st.session_state.ocr_results_data):
            confidence_color = self.get_confidence_color(data['confidence'])
            
            st.markdown(f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin: 5px 0; border-radius: 5px;">
                <strong>Block {i+1}:</strong><br>
                <span style="font-size: 1.1em;">{data['text']}</span><br>
                <small style="color: {confidence_color};">
                    Confidence: {data['confidence']:.2f} ({self.get_confidence_label(data['confidence'])})
                </small>
            </div>
            """, unsafe_allow_html=True)
    
    def render_confidence_analysis(self):
        """Render confidence analysis"""
        if not st.session_state.ocr_confidence_scores:
            st.warning("No confidence data available.")
            return
        
        # Confidence distribution
        confidence_ranges = {
            'High (0.8+)': sum(1 for c in st.session_state.ocr_confidence_scores if c >= 0.8),
            'Medium (0.5-0.8)': sum(1 for c in st.session_state.ocr_confidence_scores if 0.5 <= c < 0.8),
            'Low (<0.5)': sum(1 for c in st.session_state.ocr_confidence_scores if c < 0.5)
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Confidence Distribution:**")
            for range_label, count in confidence_ranges.items():
                st.write(f"• {range_label}: {count} blocks")
        
        with col2:
            st.markdown("**Quality Assessment:**")
            avg_conf = np.mean(st.session_state.ocr_confidence_scores)
            quality = self.get_quality_assessment(avg_conf)
            st.write(f"• Overall Quality: {quality}")
            st.write(f"• Average Confidence: {avg_conf:.2f}")
        
        # Show low confidence text blocks
        low_conf_blocks = [d for d in st.session_state.ocr_results_data if d['confidence'] < 0.5]
        if low_conf_blocks:
            st.markdown("**⚠️ Low Confidence Text Blocks:**")
            for block in low_conf_blocks:
                st.write(f"• \"{block['text']}\" (Confidence: {block['confidence']:.2f})")
    
    def render_download_options(self):
        """Render download options for extracted text"""
        st.markdown("---")
        st.subheader("💾 Download Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with col1:
            st.download_button(
                "📄 Download as TXT",
                data=st.session_state.ocr_extracted_text,
                file_name=f"ocr_text_{timestamp}.txt",
                mime="text/plain"
            )
        
        with col2:
            # Create detailed report
            detailed_report = self.create_detailed_report()
            st.download_button(
                "📊 Download Report",
                data=detailed_report,
                file_name=f"ocr_report_{timestamp}.txt",
                mime="text/plain"
            )
        
        with col3:
            # Create JSON data
            json_data = self.create_json_export()
            st.download_button(
                "📋 Download JSON",
                data=json_data,
                file_name=f"ocr_data_{timestamp}.json",
                mime="application/json"
            )
        
        with col4:
            if st.button("🔄 Clear Results"):
                self.clear_results()
    
    def render_tips_section(self):
        """Render tips and guidelines for better OCR results"""
        with st.expander("💡 Tips for Better OCR Results"):
            st.markdown("""
            **For Best Results:**
            
            📸 **Image Quality:**
            • Use high-resolution images (300+ DPI)
            • Ensure good lighting and contrast
            • Avoid blurry or distorted images
            
            📝 **Text Characteristics:**
            • Clear, readable fonts work best
            • Avoid highly stylized or decorative fonts
            • Ensure text is horizontal and not rotated
            
            🖼️ **Image Preparation:**
            • Crop to focus on text areas
            • Remove unnecessary backgrounds
            • Ensure text is not too small or too large
            
            ⚙️ **Processing Tips:**
            • Try different image formats if results are poor
            • Consider image enhancement tools for poor quality images
            • Break large documents into smaller sections
            """)
    
    def get_confidence_color(self, confidence):
        """Get color based on confidence score"""
        if confidence >= 0.8:
            return "green"
        elif confidence >= 0.5:
            return "orange"
        else:
            return "red"
    
    def get_confidence_label(self, confidence):
        """Get confidence label"""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def get_quality_assessment(self, avg_confidence):
        """Get overall quality assessment"""
        if avg_confidence >= 0.8:
            return "Excellent"
        elif avg_confidence >= 0.65:
            return "Good"
        elif avg_confidence >= 0.5:
            return "Fair"
        else:
            return "Poor"
    
    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def create_detailed_report(self):
        """Create detailed OCR report"""
        report = f"""OCR EXTRACTION REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
========================

STATISTICS:
• Total Words: {len(st.session_state.ocr_extracted_text.split())}
• Total Characters: {len(st.session_state.ocr_extracted_text)}
• Text Blocks: {len(st.session_state.ocr_results_data)}
• Average Confidence: {np.mean(st.session_state.ocr_confidence_scores):.2f}

EXTRACTED TEXT:
{st.session_state.ocr_extracted_text}

DETAILED RESULTS:
"""
        
        for i, data in enumerate(st.session_state.ocr_results_data):
            report += f"\nBlock {i+1}:\n"
            report += f"Text: {data['text']}\n"
            report += f"Confidence: {data['confidence']:.2f}\n"
            report += f"Quality: {self.get_confidence_label(data['confidence'])}\n"
            report += "-" * 30 + "\n"
        
        return report
    
    def create_json_export(self):
        """Create JSON export of OCR data"""
        import json
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_words": len(st.session_state.ocr_extracted_text.split()),
                "total_characters": len(st.session_state.ocr_extracted_text),
                "text_blocks": len(st.session_state.ocr_results_data),
                "average_confidence": float(np.mean(st.session_state.ocr_confidence_scores)) if st.session_state.ocr_confidence_scores else 0
            },
            "extracted_text": st.session_state.ocr_extracted_text,
            "detailed_results": [
                {
                    "block_id": i + 1,
                    "text": data['text'],
                    "confidence": float(data['confidence']),
                    "quality": self.get_confidence_label(data['confidence'])
                }
                for i, data in enumerate(st.session_state.ocr_results_data)
            ]
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def clear_results(self):
        """Clear all OCR results"""
        st.session_state.ocr_extracted_text = ""
        st.session_state.ocr_confidence_scores = []
        st.session_state.ocr_results_data = []
        st.rerun()

# Function to create and return OCR tool instance
def create_ocr_tool():
    """Create and return an OCR tool instance"""
    return OCRTool()

