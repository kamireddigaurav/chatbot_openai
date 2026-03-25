import streamlit as st
from PyPDF2 import PdfReader
import os
import requests
import time

# Try to get API key from environment, fallback to hardcoded (for development only)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# OpenAI API endpoint
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

# Demo mode - set to True to test without API calls
DEMO_MODE = False

def validate_api_key(api_key):
    """Validate API key format"""
    if not api_key:
        return False, "API key is empty"
    if not api_key.startswith("sk-"):
        return False, "API key doesn't start with 'sk-'"
    if len(api_key) < 20:
        return False, "API key is too short"
    return True, "API key format looks valid"

def call_openai_api(prompt, max_retries=3):
    """Call OpenAI API with retry logic"""
    
    # Demo mode for testing
    if DEMO_MODE:
        time.sleep(1)
        return "This is a demo response. The chatbot is working! To use real answers, please verify your OpenAI API key and ensure your account has credits.", None
    
    # Validate API key first
    is_valid, message = validate_api_key(OPENAI_API_KEY)
    if not is_valid:
        return None, f"⚠️ API Key Issue: {message}\n\nPlease check:\n1. API key is correct\n2. Account has credits\n3. Account is verified"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that answers questions about documents."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000,
        "temperature": 0
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(OPENAI_API_URL, headers=headers, json=payload, timeout=30)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                if attempt < max_retries - 1:
                    st.warning(f"⏳ Rate limited. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    return None, """❌ OpenAI API Rate Limited
                    
This usually means:
1. **Invalid API Key** - Check your key at openai.com/account/api-keys
2. **No Credits** - Add credits to your OpenAI account
3. **Account Not Verified** - Verify your email and payment method
4. **Usage Quota Exceeded** - Check your usage limits

🔧 Quick Fix:
- Visit: https://platform.openai.com/account/api-keys
- Verify your API key is active
- Check billing at: https://platform.openai.com/account/billing/overview
- Try again in a few minutes"""
            
            # Handle other errors
            if response.status_code == 401:
                return None, "❌ Authentication Error: Invalid API key. Please verify your OpenAI API key."
            
            if response.status_code == 403:
                return None, "❌ Permission Error: Your account doesn't have access to this API."
            
            response.raise_for_status()  # Raise exception for bad status codes
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return answer, None
            
        except requests.exceptions.Timeout:
            return None, "⏱️ Request to OpenAI API timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return None, "🌐 Connection error. Check your internet connection and try again."
        except requests.exceptions.RequestException as e:
            return None, f"🔴 API Error: {str(e)}"
        except KeyError:
            return None, "❌ Error parsing OpenAI response. The API returned an unexpected format."
        except Exception as e:
            return None, f"❌ Unexpected error: {str(e)}"
    
    return None, "Failed to get response after multiple retries."

# Page title
st.header("📄 PDF Chatbot")
st.write("Upload a PDF file and ask questions about it!")

# Sidebar for file upload
with st.sidebar:
    st.title("📁 Upload Document")
    file = st.file_uploader("Choose a PDF file", type="pdf")

# Main content
if file is not None:
    # Extract text from PDF
    st.info("📖 Processing PDF...")
    pdf_reader = PdfReader(file)
    text = ""
    
    for page_num, page in enumerate(pdf_reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += f"\n--- Page {page_num + 1} ---\n{page_text}"
    
    if not text:
        st.error("Could not extract text from PDF. Please try a different file.")
    else:
        st.success(f"✅ Extracted text from {len(pdf_reader.pages)} pages")
        
        # Break text into chunks for context
        chunk_size = 3000
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Get user question
        user_question = st.text_input("❓ Ask a question about the PDF:")
        
        if user_question:
            try:
                # Create a context from relevant chunks (simple search)
                context = text[:6000] if len(text) > 6000 else text
                
                # Create the prompt
                prompt = f"""You are a helpful assistant that answers questions about a document.

Document content:
{context}

Question: {user_question}

Please answer the question based on the document content provided. If the information is not in the document, say so."""
                
                # Call OpenAI API using direct HTTP request with retry logic
                try:
                    st.write("🤔 Thinking...")
                    answer, error = call_openai_api(prompt)
                    
                    if error:
                        st.error(f"OpenAI API Error: {error}")
                    else:
                        st.subheader("💡 Answer:")
                        st.write(answer)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
else:
    st.info("👈 Please upload a PDF file to get started!")
