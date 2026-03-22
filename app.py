import streamlit as st
import os
from PIL import Image
import requests
from io import BytesIO

st.set_page_config(page_title="CodeCraft", page_icon="🤖", layout="wide")

# --- Hugging Face Inference API configuration ---
HF_API_TOKEN = st.secrets.get("hf_api_token", "") or os.getenv("HF_API_TOKEN")  # You must set this in Streamlit Community sharing secrets.
HF_API_URL = "https://router.huggingface.co/models/bigcode/starcoderbase"

def hf_generate_completion(system_prompt, user_prompt, temperature=0.3, max_tokens=512):
    """Query the Hugging Face text-generation inference endpoint via API."""
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    prompt = f"{system_prompt}\n\n{user_prompt.strip()}\n"

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            # The following are for StarCoder/causalLM
            "return_full_text": True,
            "do_sample": temperature > 0
        },
        "options": {
            "wait_for_model": True
        }
    }
    resp = requests.post(HF_API_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        return f"HuggingFace API Error: {resp.status_code} {resp.text}"
    try:
        completions = resp.json()
        # HF API format: [{'generated_text': ...}]
        text = ""
        if isinstance(completions, list) and len(completions) and "generated_text" in completions[0]:
            text = completions[0]["generated_text"]
        elif isinstance(completions, dict) and "generated_text" in completions:
            text = completions["generated_text"]
        else:
            return "Model did not return expected API format (no 'generated_text')."
        # Remove the prompt part echoed if present:
        out = text[len(prompt):] if text.startswith(prompt) else text
        return out.strip()
    except Exception as e:
        return f"API response parse error: {str(e)}\nRaw: {resp.text}"

# Code translation and manipulation functions using HuggingFace API

def convert_code_pro(input_code, input_lang, output_lang):
    system = (
        "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    )
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"
    return hf_generate_completion(system, prompt, temperature=0.3)

def generate_code(input_code, output_lang):
    system = (
        f"You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate codes maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language {output_lang}. Avoid adding unnecessary comments or notes."
    )
    prompt = f"Generate the following {output_lang} code with the these instructions :\n\n{input_code} . \n Ensure the generated code is functional and idiomatic of the {output_lang} language."
    return hf_generate_completion(system, prompt, temperature=0.3)

def convert_code_base(input_code, input_lang, output_lang):
    system = (
        "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    )
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"
    return hf_generate_completion(system, prompt, temperature=0)

def convert_code_random(input_code, input_lang, output_lang):
    system = (
        "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    )
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"
    return hf_generate_completion(system, prompt, temperature=1)

def explain_code(input_code, input_lang):
    system = (
        "You are an AI assistant that excels in explaining complex codes across various programming languages. Your explanations should be detailed, covering fundamental concepts and key points, and presented in a way that is accessible to beginners."
    )
    prompt = f"Please explain the following {input_lang} code. Highlight the main concepts, the purpose of the code, and any advanced programming techniques used:\n\n{input_code}"
    return hf_generate_completion(system, prompt, temperature=0.5)

def optimize(input_code, input_lang):
    system = (
        "You are an experienced code developer proficient in various programming languages. Your goal is to modify the given code to a more efficient and optimized version based on the context maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    )
    prompt = f"Understand the context and optimize the {input_lang} code into a most functional code, ensuring the optimized code is functional and idiomatic of the target language:\n\n{input_code}"
    return hf_generate_completion(system, prompt, temperature=0.3)

def generate_ui(uploaded_file, output_lang):
    system = (
        "You are an AI assistant that excels in full-stack development and UI design. Your goal is to generate codes which can render a user-friendly and responsive UI based on the uploaded file content in different front-end languages."
    )
    prompt = f"Please analyze the following {uploaded_file}. Understand the purpose of the UI interface in the file and generate an equivalent code in {output_lang}"
    return hf_generate_completion(system, prompt, temperature=0.5)

def apply_modifications(output_code, modifications):
    system = (
        "You are an experienced code developer proficient various programming languages. You can understand the code and modify it accordingly by fixing the errors based on the context."
    )
    prompt = f"Apply the following {modifications} to the:\n\n {output_code}"
    return hf_generate_completion(system, prompt, temperature=0.3)

# UI layout

# Initializing session state variables
if 'generate_clicked' not in st.session_state:
    st.session_state.generate_clicked = False
if 'convert_clicked' not in st.session_state:
    st.session_state.convert_clicked = False
if 'suggestion1_clicked' not in st.session_state:
    st.session_state.suggestion1_clicked = False
if 'suggestion2_clicked' not in st.session_state:
    st.session_state.suggestion2_clicked = False
if 'debug_clicked' not in st.session_state:
    st.session_state.debug_clicked = False
if 'output_code' not in st.session_state:
    st.session_state['output_code'] = ""

col1, col2, col3, col4, col5 = st.columns(5)
cola, colb, colc, cold = st.columns(4)

st.title("CodeCraft : Your AI Coding Assistant")
st.caption("Unlock your coding skills with the new AI-powered coding assistant that helps you generate, convert, and optimize your codes supporting multiple programming languages.")
st.write("\n")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([" Generate " , " Convert " , "  Explain " , " Optimize " , " Debug " , " UI Generator"])

st.markdown("""
<style>
.stTabs [data-baseweb="tab"] {
    font-size: 20px;
    font-weight: bold;
    margin-right: 20px;
}
</style>
""", unsafe_allow_html=True)

######################## Generate #########################################################

with tab1:
   st.write("Enter your inputs for the code generation")
   input_code = st.text_area("Type your query", height=200, placeholder= "Example: Write a Python code to calculate the factorial of a number")
   output_lang = st.selectbox("Output Language", ['Python', 'Java','JavaScript', 'C++', 'SAS 9.4','R', 'SQL','VBA','Dash Plotly','ReactJS'], key = 'tab1')        

   if st.button('Generate'):
        st.session_state.generate_clicked = True
        if input_code and output_lang:
            result = generate_code(input_code, output_lang)
            st.session_state.output_code = result
            st.download_button("Download", result, f"generated_code.{output_lang}")
            st.write("The code has been Generated successfully.")              
        else :
            st.error("Please provide the code and select the languages.")

   if st.session_state.generate_clicked:
        st.text_area("Generated code", st.session_state.output_code, height = 400)
        if st.checkbox('Debug Generated code'):
            user_modifications = st.text_area("Enter your inputs here: ", height=100, placeholder="Example: Fix the indentation /n Hint: list your modifications/errors as simple points without explanations") 
            if st.button('Debug'):
                st.session_state.debug_clicked = True
                if st.session_state.output_code and user_modifications:
                    modified_code = apply_modifications(st.session_state.output_code, user_modifications)
                    st.session_state.output_code = modified_code
                    st.text_area("Modified Code", modified_code, height=400)
                    st.download_button("Download", modified_code, f"modified_code.{output_lang}")
                    st.write("The code has been modified based on your inputs")     

######################## Conversion #######################
     
with tab2:
   st.write("Insert your code for conversion into the preferred languages")
   radio_option = st.radio("Select the type of input", ['Paste your code','Upload your file'])

   if radio_option == 'Paste your code':
        input_code = st.text_area("Code to convert", height=300, placeholder="Example: \n def factorial(n): \n if n == 0: \n return 1 \n else: \n return n * factorial(n-1) \n print(factorial(5))")
        uploaded_file = None

   if radio_option == 'Upload your file': 
        uploaded_file = st.file_uploader("Upload a file", type=[
            "py", "java", "js", "cpp", "sas", "r", "sql", "vba", "dash", "react", "txt","jpg","jpeg","png","docx","doc","json","xml",
            "html","css","scss","yaml","yml","md","rst","tex","rtf","cfg","conf","config","bat","sh","cmd","bash","c","h","c++","cxx",
            "cpp","cs","csharp","m","r","rmd","rmarkdown","ipynb","py","pyc","pyo","pyd","whl","java","jsp","js","ts","tsx"
        ])
   input_lang = st.selectbox("Input Language", ['Python','Java','JavaScript', 'C++', 'SAS 9.4', 'R', 'SQL','VBA','Dash Plotly','ReactJS','Natural language','Other'])
   output_lang = st.selectbox("Output Language", ['Python','Java','JavaScript', 'C++', 'SAS 9.4','R', 'SQL','VBA','Dash Plotly','ReactJS'], key='tab2')        

   if uploaded_file is not None:
    input_code = uploaded_file.getvalue().decode("utf-8")
    st.write("Uploaded script")
    st.code(input_code, language=input_lang)

   if st.button('Convert'):
        st.session_state.convert_clicked = True
        if input_code and input_lang and output_lang:
            result = convert_code_pro(input_code, input_lang, output_lang)
            st.session_state.output_code = result
            st.download_button("Download", result, f"converted_code.{output_lang}")
            st.write("The code has been translated successfully.")
        else:          
            st.error("Please provide the code and select the languages.")

   if st.session_state.convert_clicked:
        st.text_area("Converted code", st.session_state.output_code, height = 400)

        if st.checkbox('Debug Converted code'):
            user_modifications = st.text_area("Enter the required modifications here: ", height=100, placeholder="Example: Fix the indentation /n Hint: list your modifications/errors as simple points without explanations")
            if st.button('Debug Converted code'):
                st.session_state.debug_clicked = True
                if st.session_state.output_code and user_modifications:
                    modified_code = apply_modifications(st.session_state.output_code, user_modifications)
                    st.session_state.output_code = modified_code
                    st.text_area("Modified Code", modified_code, height=350)
                    st.download_button("Download ", modified_code, f"modified_code.{output_lang}")
                    st.write("The code has been modified based on required modifications")  

#################### Explain #############  

with  tab3:
    st.write("Insert your code for explanation and summary")
    input_code = st.text_area("Code to explain", height=300, placeholder="Example: \n def factorial(n): \n if n == 0: \n return 1 \n else: \n return n * factorial(n-1) \n print(factorial(5))")
    input_lang = st.selectbox("Input Language", ['Python','Java','JavaScript', 'C++', 'SAS 9.4', 'R', 'SQL','VBA','Dash Plotly','ReactJS','Natural language','Other'], key='tab3')

    if st.button('Explain'):
        if input_code and input_lang:
            result = explain_code(input_code, input_lang)
            st.text_area("Summary of the above code", result, height=600)
        else:
            st.error("Please provide the code or file and select the languages.")    

###################### Optimize #############      

with tab4:
   st.write("Optimize your messy codes for better performance")
   input_code = st.text_area("Please insert your code to optimize", height=400)
   input_lang = st.selectbox("Input Language", ['Python','Java','JavaScript', 'C++', 'SAS 9.4', 'R', 'SQL','VBA','Dash Plotly','ReactJS','Natural language','Other'], key='tab4')

   if st.button('Optimize'):
    if input_code and input_lang:
        result = optimize(input_code, input_lang)
        st.text_area("Optimized Code", result, height=400)
    else:
        st.error("Please provide the code or file and select the languages.")

###################### Debug ##################
   
with tab5:
   st.write("Fix your codes and debug the errors for better performance")
   input_code = st.text_area("Please insert your code to debug", height=400)
   input_lang = st.selectbox("Input Language", ['Python','Java','JavaScript', 'C++', 'SAS 9.4', 'R', 'SQL','VBA','Dash Plotly','ReactJS','Natural language','Other'], key='tab5')

   if st.button('Modify'):
    if input_code and input_lang:
        result = apply_modifications(input_code, input_lang)
        st.text_area("Modified code", result, height=400)
    else:
        st.error("Please provide the code or file and select the languages.")

################# UI Generation #################     

with tab6:
   st.write("Generate UI code based on the uploaded file content")
   radio_option = st.radio("Select the type of input", ['Insert image link','Upload your file']) 

   if radio_option == 'Insert image link':
        uploaded_file = st.text_area("Paste image endpoint", placeholder="https://www.example.com/image.jpg")
        if uploaded_file:
            response = requests.get(uploaded_file)
            if response.status_code == 200:
                image = Image.open(requests.get(uploaded_file, stream=True).raw)
                image_resize = image.resize((200,200))
                st.image(image_resize, caption='Image from URL', use_column_width=False)
            else:
                st.error("Error : Could not fetch image from the given url.")    

   elif radio_option == 'Upload your file':
       uploaded_file = st.file_uploader("Upload your image for the agent to analyze", type=["jpg","jpeg","png","html","css","pptx","ppt","php","php3","php4","php5","php7","phps","phtml","php-s"])
       if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image_resize = image.resize((200,200))
        st.image(image_resize, caption='Uploaded Image', use_column_width=False)

   output_lang = st.selectbox("Output Language", ['HTML','CSS','Dash Plotly','ReactJS', 'R SHiny'])
   
   if st.button('Generate UI'):
     if uploaded_file and output_lang:
        ui = generate_ui(uploaded_file, output_lang)
        st.text_area("Generated UI Code", ui, height=400)   
     else:
        st.error("Please provide the code or file and select the languages.")     

#### NOTES #########
