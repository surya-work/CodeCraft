import streamlit as st
import openai
from azure.identity import DefaultAzureCredential
import os
from openai import ChatCompletion
from PIL import Image
import requests
from io import BytesIO
# import pyperclip


st.set_page_config(page_title="CodeCraft", page_icon="🤖", layout="wide") 



# Open ai access Azure

credentials = DefaultAzureCredential()
token = credentials.get_token("api://2a459df9-d8e1-43e0-998e-320abbe581d0/.default")  
openai.api_type = "azure_ad"
openai.api_key = token.token
openai.api_base = "https://openai.work.iqvia.com/cse/prod/proxy/azure/az-cs-caet-rws-ida-openai-p01"
openai.api_version = "2023-03-15-preview"

# Openai function call neutral version
def convert_code_pro(input_code, input_lang, output_lang):

    system = "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":system},
             {"role":"user","content":prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def generate_code(input_code, output_lang):

    system = f"You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate codes maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language {output_lang}. Avoid adding unnecessary comments or notes."
    prompt = f"Generate the following {output_lang} code with the these instructions :\n\n{input_code} . \n Ensure the generated code is functional and idiomatic of the {output_lang} language."

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":system},
             {"role":"user","content":prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# Openai function call base version
def convert_code_base(input_code, input_lang, output_lang):

    system = "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":f"{system}"},
             {"role":"user","content":f"{prompt}"}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()

# Openai function call random version
def convert_code_random(input_code, input_lang, output_lang):

    system = "You are an experienced code developer proficient in various programming languages. Your goal is to generate accurate code translations maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    prompt = f"Translate the following {input_lang} code into {output_lang} code, ensuring the translated code is functional and idiomatic of the target language:\n\n{input_code}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":f"{system}"},
             {"role":"user","content":f"{prompt}"}],
        temperature=1,
    )
    return response.choices[0].message.content.strip()

# Code explanation and summary
def explain_code(input_code, input_lang):

    system = "You are an AI assistant that excels in explaining complex codes across various programming languages. Your explanations should be detailed, covering fundamental concepts and key points, and presented in a way that is accessible to beginners."
    prompt = f"Please explain the following {input_lang} code. Highlight the main concepts, the purpose of the code, and any advanced programming techniques used:\n\n{input_code}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":f"{system}"},
             {"role":"user","content":f"{prompt}"}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

# Code optimization
def optimize(input_code, input_lang):

    system = "You are an experienced code developer proficient in various programming languages. Your goal is to modify the given code to a more efficient and optimized version based on the context maintaining accuracy, functionality, efficiency and adhere to the idiomatic conventions of the output language. Avoid adding unnecessary comments or notes."
    prompt = f"Understand the context and optimize the {input_lang} code into a most functional code, ensuring the optimized code is functional and idiomatic of the target language:\n\n{input_code}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":system},
             {"role":"user","content":prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def generate_ui(uploaded_file, output_lang):

    system = "You are an AI assistant that excels in full-stack development and UI design. Your goal is to generate codes which can render a user-friendly and responsive UI based on the uploaded file content in different front-end languages."
    prompt = f"Please analyze the following {uploaded_file}.Understand the purpose of the UI interface in the file and generate a equivalent code in {output_lang}"

    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":f"{system}"},
             {"role":"user","content":f"{prompt}"}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def apply_modifications(output_code, modifications):
    system = "You are an experienced code developer proficient various programming languages. You can understand the code and modify it accordingly by fixing the errors based on the context."
    prompt = f"Apply the following {modifications} to the:\n\n {output_code}"
    # modified_code = result + "\n" + modifications
    response = ChatCompletion.create(
        model="gpt-4",
        deployment_id="GPT-4",
        messages= [
             {"role":"system","content":system},
             {"role":"user","content":prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

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
#    st.download_button("Download", input_code, f"input_code.txt")
   output_lang = st.selectbox("Output Language", ['Python', 'Java','JavaScript', 'C++', 'SAS 9.4','R', 'SQL','VBA','Dash Plotly','ReactJS'], key = 'tab1')        
#    copy_button = st.button("Copy to clipboard")

#    if copy_button:
#         pyperclip.copy(input_code)
#         st.write("The input code has been copied to the clipboard")

   if st.button('Generate'):
        st.session_state.generate_clicked = True
        if input_code and output_lang:
            result = generate_code(input_code, output_lang)
            st.session_state.output_code = result
            # output_code = st.text_area("Code Generated",result, height=300)
            # output_code.code(result, language=output_lang)
            # st.text_area("Generated code",result, height=400)
            st.download_button("Download", result, f"generated_code.{output_lang}")
            st.write("The code has been Generated successfully.")              
        else :
            st.error("Please provide the code and select the languages.")

   if st.session_state.generate_clicked:
        st.text_area("Generated code", st.session_state.output_code, height = 400)
        # if cola.button('Suggestion1'):
        #     st.session_state.suggestion1_clicked = True
        #     result = convert_code_base(input_code, input_lang, output_lang)
        #     st.text_area("Converted Code", result, height=400)
        # if colb.button('Suggestion2'):
        #     st.session_state.suggestion2_clicked = True
        #     result = convert_code_random(input_code, input_lang, output_lang)
        #     st.text_area("Converted Code", result, height=400)
        if st.checkbox('Debug Generated code'):
            user_modifications = st.text_area("Enter your inputs here: ", height=100, placeholder="Example: Fix the indentation /n Hint: list your modifications/errors as simple points without explanations") 
            if st.button('Debug'):
                st.session_state.debug_clicked = True
                # st.session_state.output_code = True
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
        uploaded_file = st.file_uploader("Upload a file", type=["py", "java", "js", "cpp", "sas", "r", "sql", "vba", "dash", "react", "txt","jpg","jpeg","png","docx","doc","json","xml","html","css","scss","yaml","yml","md","rst","tex","rtf","cfg","conf","config","bat","sh","cmd","bash","c","h","c++","cxx","cpp","cs","csharp","m","r","rmd","rmarkdown","ipynb","py","pyc","pyo","pyd","whl","java","jsp","js","ts","tsx"])
        # input_code = None

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
            # st.text_area("Converted code",result, height=400)
            # output_code = st.text_area("Converted Code",result, height=300)
            # output_code.code(result, language=output_lang)
            st.download_button("Download", result, f"converted_code.{output_lang}")
            st.write("The code has been translated successfully.")

        elif uploaded_file and input_lang and output_lang:
            result = convert_code_pro(uploaded_file, input_lang, output_lang)
            st.session_state.output_code = result
            # st.text_area("Converted code",result, height=400)
            # output_code = st.text_area("Converted Code",result, height=300)
            # output_code.code(result, language=output_lang)
            st.download_button("Download", result, f"converted_code.{output_lang}")
            st.write("The code has been translated successfully.")
        else:          
            st.error("Please provide the code and select the languages.")

   if st.session_state.convert_clicked:
        st.text_area("Converted code", st.session_state.output_code, height = 400)

        if st.checkbox('Debug Converted code'):
            user_modifications = st.text_area("Enter the required modifications here: ", height=100,placeholder="Example: Fix the indentation /n Hint: list your modifications/errors as simple points without explanations")
            if st.button('Debug Converted code'):
                st.session_state.debug_clicked = True
                # st.session_state.output_code = True
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
    if input_code and input_lang and output_lang:
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
                # image = Image.open(BytesIO(response.content))
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

#    uploaded_file = st.file_uploader("Upload your image for the agent to analyze", type=["jpg","jpeg","png","html","css","pptx","ppt","php","php3","php4","php5","php7","phps","phtml","php-s"])
   output_lang = st.selectbox("Output Language", ['HTML','CSS','Dash Plotly','ReactJS', 'R SHiny'])
   
   if st.button('Generate UI'):
     if uploaded_file and output_lang:
        ui = generate_ui(uploaded_file, output_lang)
        st.text_area("Generated UI Code", ui, height=400)   
     else:
        st.error("Please provide the code or file and select the languages.")     

#### NOTES #########
