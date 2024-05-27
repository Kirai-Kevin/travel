import streamlit as st
import replicate
import os
from dotenv import load_dotenv
import webbrowser
# from config import REPLICATE_API_KEY

load_dotenv()

# Set the app's title
st.set_page_config(page_title="Travel Assistant")

REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY")

# Function to check if the API key is valid
def is_valid_api_key(api_key):
    return api_key.startswith('r8_') and len(api_key) == 40

# Function to set API key
def set_api_key(api_key):
    if is_valid_api_key(api_key):
        os.environ['REPLICATE_API_TOKEN'] = api_key
        st.success('API key set!', icon='✅')
        return True
    else:
        st.error('Invalid API key! Please enter a valid Replicate API key.')
        return False

# Sidebar setup
with st.sidebar:
    st.title("Travel Assistant")
    
    use_own_api_key = st.checkbox("Use your own API key")
    
    if use_own_api_key:
        custom_api_key = st.text_input('Enter your Replicate API Key:', type='password', key='custom_replicate_api_key')
        if custom_api_key:
            set_api_key(custom_api_key)
    else:
        if is_valid_api_key(REPLICATE_API_KEY):
            os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_KEY
            st.success('Default API key loaded from config!', icon='✅')
        else:
            st.warning('Default API key is not valid. Please enter your own API key.')

    # Hidden model selection and parameters
    with st.empty():
        st.subheader('Models and Parameters')
        selected_model = st.selectbox('Choose a Llama2 model', ['Llama2-7B', 'Llama2-13B'], key='selected_model')
        llm = {
            'Llama2-7B': 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea',
            'Llama2-13B': 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
        }.get(selected_model)

    # 5-star rating system
    st.subheader('Rate the Assistant')
    rating = st.slider('Rate your experience', 1, 5, 3)
    if st.button('Submit Rating'):
        st.write(f'Thank you for rating us {rating} stars!')

# Initialize session state for chat messages if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Function to clear chat history
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    st.experimental_rerun()  # Rerun the app to clear the chat history
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function to check if the question is relevant
def is_relevant_question(prompt_input):
    relevant_keywords = ["travel", "tourism", "wildlife", "hotels", "destination", "adventure", "safari", "bird", "park", "species", "reserve", "sanctuary", "animal", "food", "culinary", "sightseeing", "trails", "hiking", "luxury", "beach", "pet-friendly", "visit", "resort"]
    prompt_lower = prompt_input.lower()
    return any(keyword in prompt_lower for keyword in relevant_keywords)

# Function to generate LLaMA2 response
def generate_llama2_response(prompt_input):
    if not is_relevant_question(prompt_input):
        return ["I'm sorry, I can only answer questions regarding travel, tourism, wildlife, and hotels."]

    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'.\n\n"
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    output = replicate.run(
        llm,  # Use the selected model
        input={"prompt": f"{string_dialogue} {prompt_input}\nAssistant: ", "temperature": 0.1, "top_p": 0.9, "max_length": 120, "repetition_penalty": 1.0}
    )
    return output
    #output_response = output[0]["generated_text"] if isinstance(output, list) and len(output) > 0 else ""
    #return [output_response]

# Chat input and response generation
if 'REPLICATE_API_TOKEN' in os.environ:
    replicate_api = os.environ['REPLICATE_API_TOKEN']
    prompt = st.text_input("You:", key="user_input")
    if st.button("Send", key="send_button"):
        if prompt.strip() == "":
            st.warning("Please enter a question.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                response = generate_llama2_response(prompt)
                full_response = ''.join(response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def open_blog():
    webbrowser.open_new_tab("https://main--dhub-blog02.netlify.app/")

st.sidebar.button("Back to Blog", on_click=open_blog)
