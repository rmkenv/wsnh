import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
import io
from PIL import Image
import zipfile
import shutil
from st_paywall import add_auth

# Define functions (keep your existing functions here)
# ...

# Streamlit app
st.title("Append PDFs or Word Documents to Word Documents")

# Check if required secrets are present
required_secrets = ['client_id', 'client_secret', 'redirect_url', 'bmac_api_key', 'bmac_link']
missing_secrets = [secret for secret in required_secrets if secret not in st.secrets]

if missing_secrets:
  st.error(f"Missing required secrets: {', '.join(missing_secrets)}. Please check your secrets.toml file or Streamlit Cloud secrets configuration.")
else:
  # Add authentication
  try:
      add_auth()
  except Exception as e:
      st.error(f"Error in authentication: {str(e)}")
  else:
      # Check if user is authenticated
      if 'email' in st.session_state:
          st.write(f"Welcome, {st.session_state.email}!")

          # Upload zip file
          zip_file = st.file_uploader("Upload ZIP file containing Word documents", type=["zip"])
          # Choose file type to append
          file_type = st.selectbox("Select file type to append", ["PDF", "Word Document"])
          # Upload multiple files
          file_types = {"PDF": "pdf", "Word Document": "docx"}
          files = st.file_uploader(f"Upload {file_type} files to append", type=[file_types[file_type]], accept_multiple_files=True)

          if st.button("Process"):
              if zip_file and files:
                  zip_path = os.path.join("uploaded_files", zip_file.name)
                  os.makedirs("uploaded_files", exist_ok=True)

                  with open(zip_path, "wb") as f:
                      f.write(zip_file.getbuffer())

                  file_paths = []
                  for file in files:
                      file_path = os.path.join("uploaded_files", file.name)
                      with open(file_path, "wb") as f:
                          f.write(file.getbuffer())
                      file_paths.append(file_path)

                  output_zip_path = os.path.join("uploaded_files", "output.zip")
                  process_zip(zip_path, file_paths, output_zip_path, file_types[file_type])

                  with open(output_zip_path, "rb") as f:
                      st.download_button("Download processed ZIP", f, file_name="processed_documents.zip")

                  st.success(f"{file_type}s appended to Word documents in {output_zip_path} successfully.")
                  shutil.rmtree("uploaded_files")
              else:
                  st.error("Please upload both a ZIP file and at least one file to append.")
      else:
          st.warning("Please log in to access this feature.")
          st.markdown(f"[Subscribe Now]({st.secrets.bmac_link})")

# For debugging purposes, you can uncomment the following line to see the contents of st.secrets
# st.write(st.secrets)
