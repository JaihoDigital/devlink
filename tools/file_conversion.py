import streamlit as st
import pandas as pd
import json
import base64
from PIL import Image
import io
import zipfile
import tempfile
import os

try:
    from docx import Document
    from docx2pdf import convert
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class FileConverter:
    def __init__(self):
        self.supported_conversions = {
            "Document Conversions": {
                "DOCX to PDF": {"input": "docx", "output": "pdf", "available": DOCX_AVAILABLE},
                "TXT to PDF": {"input": "txt", "output": "pdf", "available": PDF_AVAILABLE},
                "MD to HTML": {"input": "md", "output": "html", "available": True},
            },
            "Data Conversions": {
                "CSV to JSON": {"input": "csv", "output": "json", "available": True},
                "JSON to CSV": {"input": "json", "output": "csv", "available": True},
                "Excel to CSV": {"input": "xlsx", "output": "csv", "available": True},
                "CSV to Excel": {"input": "csv", "output": "xlsx", "available": True},
            },
            "Image Conversions": {
                "PNG to JPG": {"input": "png", "output": "jpg", "available": True},
                "JPG to PNG": {"input": "jpg", "output": "png", "available": True},
                "Image to Base64": {"input": "image", "output": "base64", "available": True},
                "Base64 to Image": {"input": "base64", "output": "image", "available": True},
            },
            "Text Conversions": {
                "JSON to YAML": {"input": "json", "output": "yaml", "available": True},
                "YAML to JSON": {"input": "yaml", "output": "json", "available": True},
                "CSV to HTML Table": {"input": "csv", "output": "html", "available": True},
            }
        }
    
    def render_file_converter(self):
        """Main file converter interface"""
        st.subheader("🔄 File Converter")
        
        # Display missing dependencies warning
        if not DOCX_AVAILABLE:
            st.warning("📦 Install `python-docx` and `docx2pdf` for DOCX to PDF conversion")
        if not PDF_AVAILABLE:
            st.warning("📦 Install `PyMuPDF` for advanced PDF operations")
        
        # Conversion type selection
        conversion_categories = list(self.supported_conversions.keys())
        selected_category = st.selectbox("Select Conversion Category", conversion_categories)
        
        conversions = self.supported_conversions[selected_category]
        available_conversions = [k for k, v in conversions.items() if v["available"]]
        
        if not available_conversions:
            st.error("No conversions available in this category. Please install required dependencies.")
            return
        
        selected_conversion = st.selectbox("Select Conversion Type", available_conversions)
        
        # Get conversion details
        conversion_info = conversions[selected_conversion]
        input_format = conversion_info["input"]
        output_format = conversion_info["output"]
        
        st.info(f"Converting from **{input_format.upper()}** to **{output_format.upper()}**")
        
        # File upload or text input based on conversion type
        if input_format == "base64":
            self.handle_base64_input(selected_conversion)
        elif input_format in ["txt", "md", "json", "yaml"]:
            self.handle_text_input(selected_conversion, input_format, output_format)
        else:
            self.handle_file_input(selected_conversion, input_format, output_format)
    
    def handle_file_input(self, conversion_type, input_format, output_format):
        """Handle file upload conversions"""
        file_types = {
            "docx": ["docx"],
            "csv": ["csv"],
            "xlsx": ["xlsx", "xls"],
            "json": ["json"],
            "png": ["png"],
            "jpg": ["jpg", "jpeg"],
            "image": ["png", "jpg", "jpeg", "bmp", "gif", "tiff"]
        }
        
        uploaded_file = st.file_uploader(
            f"Upload {input_format.upper()} file",
            type=file_types.get(input_format, [input_format])
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            if st.button(f"🔄 Convert to {output_format.upper()}"):
                with st.spinner("Converting file..."):
                    try:
                        converted_data = self.convert_file(
                            uploaded_file, conversion_type, input_format, output_format
                        )
                        
                        if converted_data:
                            self.provide_download(converted_data, output_format, uploaded_file.name)
                        else:
                            st.error("Conversion failed!")
                            
                    except Exception as e:
                        st.error(f"Conversion error: {str(e)}")
    
    def handle_text_input(self, conversion_type, input_format, output_format):
        """Handle text input conversions"""
        st.markdown(f"#### Input {input_format.upper()} content:")
        
        if input_format == "json":
            placeholder = '{"name": "John", "age": 30, "city": "New York"}'
        elif input_format == "yaml":
            placeholder = "name: John\nage: 30\ncity: New York"
        elif input_format == "md":
            placeholder = "# My Document\n\nThis is **bold** text."
        else:
            placeholder = "Enter your text here..."
        
        text_input = st.text_area(
            f"Enter {input_format.upper()} content",
            height=300,
            placeholder=placeholder
        )
        
        if text_input and st.button(f"🔄 Convert to {output_format.upper()}"):
            with st.spinner("Converting..."):
                try:
                    converted_data = self.convert_text(
                        text_input, conversion_type, input_format, output_format
                    )
                    
                    if converted_data:
                        st.markdown(f"#### Converted {output_format.upper()} content:")
                        
                        if output_format == "html":
                            st.components.v1.html(converted_data, height=400, scrolling=True)
                        else:
                            st.code(converted_data, language=output_format)
                        
                        # Download button
                        st.download_button(
                            f"⬇️ Download {output_format.upper()}",
                            converted_data,
                            f"converted.{output_format}",
                            f"text/{output_format}"
                        )
                    else:
                        st.error("Conversion failed!")
                        
                except Exception as e:
                    st.error(f"Conversion error: {str(e)}")
    
    def handle_base64_input(self, conversion_type):
        """Handle base64 input conversion"""
        st.markdown("#### Enter Base64 string:")
        base64_input = st.text_area(
            "Base64 string",
            height=200,
            placeholder="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        )
        
        if base64_input and st.button("🔄 Convert to Image"):
            try:
                # Remove data URL prefix if present
                if "base64," in base64_input:
                    base64_input = base64_input.split("base64,")[1]
                
                # Decode base64
                image_data = base64.b64decode(base64_input)
                image = Image.open(io.BytesIO(image_data))
                
                st.image(image, caption="Converted Image", use_column_width=True)
                
                # Download button
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                
                st.download_button(
                    "⬇️ Download Image",
                    img_buffer.getvalue(),
                    "converted_image.png",
                    "image/png"
                )
                
            except Exception as e:
                st.error(f"Conversion error: {str(e)}")
    
    def convert_file(self, uploaded_file, conversion_type, input_format, output_format):
        """Convert uploaded file to target format"""
        try:
            if conversion_type == "DOCX to PDF":
                return self.docx_to_pdf(uploaded_file)
            elif conversion_type == "CSV to JSON":
                return self.csv_to_json(uploaded_file)
            elif conversion_type == "JSON to CSV":
                return self.json_to_csv(uploaded_file)
            elif conversion_type == "Excel to CSV":
                return self.excel_to_csv(uploaded_file)
            elif conversion_type == "CSV to Excel":
                return self.csv_to_excel(uploaded_file)
            elif conversion_type in ["PNG to JPG", "JPG to PNG"]:
                return self.convert_image_format(uploaded_file, output_format)
            elif conversion_type == "Image to Base64":
                return self.image_to_base64(uploaded_file)
            else:
                st.error(f"Conversion type '{conversion_type}' not implemented")
                return None
                
        except Exception as e:
            st.error(f"File conversion error: {str(e)}")
            return None
    
    def convert_text(self, text_input, conversion_type, input_format, output_format):
        """Convert text input to target format"""
        try:
            if conversion_type == "JSON to YAML":
                return self.json_to_yaml(text_input)
            elif conversion_type == "YAML to JSON":
                return self.yaml_to_json(text_input)
            elif conversion_type == "MD to HTML":
                return self.md_to_html(text_input)
            elif conversion_type == "CSV to HTML Table":
                return self.csv_text_to_html(text_input)
            else:
                st.error(f"Text conversion type '{conversion_type}' not implemented")
                return None
                
        except Exception as e:
            st.error(f"Text conversion error: {str(e)}")
            return None
    
    def docx_to_pdf(self, uploaded_file):
        """Convert DOCX to PDF"""
        if not DOCX_AVAILABLE:
            st.error("DOCX conversion dependencies not available")
            return None
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_docx:
            tmp_docx.write(uploaded_file.read())
            tmp_docx_path = tmp_docx.name
        
        # Convert to PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            tmp_pdf_path = tmp_pdf.name
        
        try:
            convert(tmp_docx_path, tmp_pdf_path)
            
            # Read PDF data
            with open(tmp_pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            # Cleanup
            os.unlink(tmp_docx_path)
            os.unlink(tmp_pdf_path)
            
            return pdf_data
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(tmp_docx_path):
                os.unlink(tmp_docx_path)
            if os.path.exists(tmp_pdf_path):
                os.unlink(tmp_pdf_path)
            raise e
    
    def csv_to_json(self, uploaded_file):
        """Convert CSV to JSON"""
        df = pd.read_csv(uploaded_file)
        return df.to_json(orient='records', indent=2)
    
    def json_to_csv(self, uploaded_file):
        """Convert JSON to CSV"""
        json_data = json.load(uploaded_file)
        df = pd.DataFrame(json_data)
        return df.to_csv(index=False)
    
    def excel_to_csv(self, uploaded_file):
        """Convert Excel to CSV"""
        df = pd.read_excel(uploaded_file)
        return df.to_csv(index=False)
    
    def csv_to_excel(self, uploaded_file):
        """Convert CSV to Excel"""
        df = pd.read_csv(uploaded_file)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()
    
    def convert_image_format(self, uploaded_file, output_format):
        """Convert image between formats"""
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (for JPG)
        if output_format.lower() == 'jpg' and image.mode != 'RGB':
            image = image.convert('RGB')
        
        output = io.BytesIO()
        image.save(output, format=output_format.upper())
        return output.getvalue()
    
    def image_to_base64(self, uploaded_file):
        """Convert image to base64 string"""
        image_data = uploaded_file.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')
        file_ext = uploaded_file.name.split('.')[-1].lower()
        return f"data:image/{file_ext};base64,{base64_string}"
    
    def json_to_yaml(self, json_text):
        """Convert JSON to YAML"""
        try:
            import yaml
            json_data = json.loads(json_text)
            return yaml.dump(json_data, default_flow_style=False)
        except ImportError:
            st.error("PyYAML not installed. Install with: pip install pyyaml")
            return None
    
    def yaml_to_json(self, yaml_text):
        """Convert YAML to JSON"""
        try:
            import yaml
            yaml_data = yaml.safe_load(yaml_text)
            return json.dumps(yaml_data, indent=2)
        except ImportError:
            st.error("PyYAML not installed. Install with: pip install pyyaml")
            return None
    
    def md_to_html(self, md_text):
        """Convert Markdown to HTML"""
        try:
            import markdown
            html = markdown.markdown(md_text)
            return f"<!DOCTYPE html><html><head><title>Converted Document</title></head><body>{html}</body></html>"
        except ImportError:
            # Simple fallback conversion
            html = md_text.replace('\n', '<br>')
            html = html.replace('**', '<strong>').replace('**', '</strong>')
            html = html.replace('*', '<em>').replace('*', '</em>')
            return f"<!DOCTYPE html><html><head><title>Converted Document</title></head><body>{html}</body></html>"
    
    def csv_text_to_html(self, csv_text):
        """Convert CSV text to HTML table"""
        lines = csv_text.strip().split('\n')
        html = "<table border='1' style='border-collapse: collapse; width: 100%;'>"
        
        for i, line in enumerate(lines):
            cells = line.split(',')
            if i == 0:
                html += "<tr style='background-color: #f2f2f2;'>"
                for cell in cells:
                    html += f"<th style='padding: 8px;'>{cell.strip()}</th>"
                html += "</tr>"
            else:
                html += "<tr>"
                for cell in cells:
                    html += f"<td style='padding: 8px;'>{cell.strip()}</td>"
                html += "</tr>"
        
        html += "</table>"
        return html
    
    def provide_download(self, data, output_format, original_filename):
        """Provide download button for converted file"""
        if isinstance(data, str):
            # Text data
            mime_type = "text/plain"
            if output_format == "json":
                mime_type = "application/json"
            elif output_format == "html":
                mime_type = "text/html"
            elif output_format == "csv":
                mime_type = "text/csv"
            
            filename = f"{original_filename.split('.')[0]}.{output_format}"
            st.download_button(
                f"⬇️ Download {output_format.upper()}",
                data,
                filename,
                mime_type
            )
        else:
            # Binary data
            mime_type = "application/octet-stream"
            if output_format == "pdf":
                mime_type = "application/pdf"
            elif output_format == "xlsx":
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif output_format in ["png", "jpg", "jpeg"]:
                mime_type = f"image/{output_format}"
            
            filename = f"{original_filename.split('.')[0]}.{output_format}"
            st.download_button(
                f"⬇️ Download {output_format.upper()}",
                data,
                filename,
                mime_type
            )
        
        st.success("✅ Conversion completed successfully!")

def create_file_converter():
    """Factory function to create File Converter instance"""
    return FileConverter()

# Main Streamlit Application
def main():
    st.set_page_config(
        page_title="File Converter",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Universal File Converter")
    st.markdown("Convert between various file formats easily and efficiently!")
    
    # Create converter instance
    converter = create_file_converter()
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 Supported Conversions")
        
        st.subheader("📄 Document Formats")
        st.write("• DOCX ↔ PDF")
        st.write("• TXT → PDF")
        st.write("• Markdown → HTML")
        
        st.subheader("📊 Data Formats")
        st.write("• CSV ↔ JSON")
        st.write("• CSV ↔ Excel")
        st.write("• JSON ↔ YAML")
        
        st.subheader("🖼️ Image Formats")
        st.write("• PNG ↔ JPG")
        st.write("• Image ↔ Base64")
        
        st.subheader("🔧 Text Utilities")
        st.write("• CSV → HTML Table")
        
        st.markdown("---")
        st.markdown("### 📦 Optional Dependencies")
        st.code("pip install python-docx docx2pdf")
        st.code("pip install PyMuPDF")
        st.code("pip install pyyaml")
        st.code("pip install markdown")
    
    # Main converter interface
    converter.render_file_converter()
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit")

#if __name__ == "__main__":
#    main()