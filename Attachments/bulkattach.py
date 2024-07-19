import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import qn
import io
from PIL import Image
import zipfile
import os
import shutil
from st_paywall import add_auth, check_auth
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Define functions (keep your existing functions here)
# ...

# Streamlit app
st.title("Append PDFs or Word Documents to Word Documents")

# Set up the OAuth flow
flow = Flow.from_client_config(
  client_config={
      "web": {
          "client_id": st.secrets["client_id"],
          "client_secret": st.secrets["client_secret"],
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
      }
  },
  scopes=['https://www.googleapis.com/auth/userinfo.email']
)
flow.redirect_uri = st.secrets["redirect_url"]

# Check if the user is authenticated
if 'credentials' not in st.session_state:
  # If not authenticated, show login button
  if st.button("Login with Google"):
      authorization_url, _ = flow.authorization_url(prompt='consent')
      st.markdown(f"[Login]({authorization_url})")
else:
  # If authenticated, show the main app
  credentials = Credentials.from_authorized_user_info(st.session_state.credentials)
  service = build('oauth2', 'v2', credentials=credentials)
  user_info = service.userinfo().get().execute()
  st.write(f"Welcome, {user_info['email']}!")

  # Your existing app logic goes here
  # Upload zip file
  zip_file = st.file_uploader("Upload ZIP file containing Word documents", type=["zip"])
  # Choose file type to append
  file_type = st.selectbox("Select file type to append", ["PDF", "Word Document"])
  # Upload multiple files
  file_types = {"PDF": "pdf", "Word Document": "docx"}
  files = st.file_uploader(f"Upload {file_type} files to append", type=[file_types[file_type]], accept_multiple_files=True)

  if st.button("Process"):
      if zip_file and files:
          # Your existing processing logic goes here
          # ...
          st.success(f"{file_type}s appended to Word documents in {output_zip_path} successfully.")
          shutil.rmtree("uploaded_files")
      else:
          st.error("Please upload both a ZIP file and at least one file to append.")

# Handle the OAuth callback
if 'code' in st.experimental_get_query_params():
  code = st.experimental_get_query_params()['code'][0]
  flow.fetch_token(code=code)
  st.session_state.credentials = flow.credentials.to_json()
  st.experimental_rerun()

# Add logout button
if 'credentials' in st.session_state:
  if st.button("Logout"):
      del st.session_state.credentials
      st.experimental_rerun()
