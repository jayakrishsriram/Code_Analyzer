import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
load_dotenv()
api_key=os.getenv('api_key')
genai.configure(api_key=api_key)

def build_prompt(data, used_for):
    input_prompt=f"""I have given the instruction below what to do follow that and give me the result:
1. Takes code snippets as input and identifies potential performance bottlenecks in detail.
2. Provides suggestions for optimization with your optimized code.
3. I want the response in one single string having the structure {{"Time and Space Complexity":"","Potential Bottlenecks":"", "Optimized code":""}} 
4. In point 3 all the three thing mentioned in the bracket should contain some content. In optimized code generate the optimized code and present it why it is the optimized code.
Also I will give you the detail what the code snippets is given here:{used_for}
Note: Make sure to give optimized code only if there is any possibility else omit it and same for Pottential Bottlenecks. If the code snippet is not given, pass a message that code is not given. 
The code snippet is:\n{data} 
 """
    return input_prompt
  

def get_gemini_repsonse(input):
    model=genai.GenerativeModel('gemini-pro')
    response=model.generate_content(input)
    return response.text

def print_response(response):
  string=""
  string+="Time and Space Complexity: \n{}\n".format(response["Time and Space Complexity"])
  string+="Potential Bottlenecks:\n{}\n".format(response["Potential Bottlenecks"])
  string+="Optimized code:\n{}\n".format(response["Optimized code"])
  print("Optimized code:\n{}\n".format(response["Optimized code"]))
  return string

def main():
    st.title("Code analyzer")
    lab=['Text Input','Document Input']
    option=st.radio("Select the type of input",options=lab)
    st.write(option)
    data=''

    used_for=st.text_area("What is the purpose of this code. This will help to optimize the code. Press (Ctrl+Enter) once you finish your input")
    
    if option=="Text Input":
        data=st.text_area("Enter your code here for further analysis. Press (Ctrl+Enter) once you finish your input")
        
    else:
        uploaded_file=st.file_uploader("Upload your document", type=['pdf','docx'], accept_multiple_files=False)
        if uploaded_file is not None:
            data=""
            file_name = uploaded_file.name
            st.write("Filename:", file_name)
            
            if file_name.endswith(".pdf"):
                st.write("Processing PDF...")
                try:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        data += page.extract_text()
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
            
            elif file_name.endswith(".docx"):
                st.write("Processing Word Document...")
                try:
                    doc = Document(uploaded_file)
                    data = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                except Exception as e:
                    st.error(f"Error reading Word document: {e}")
    if st.button("Analyze"):
        input_prompt=build_prompt(data,used_for)
        response=get_gemini_repsonse(input_prompt)
        response = json.loads(response)
        st.code(print_response(response))
    
main()