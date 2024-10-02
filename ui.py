import os
import sys
from io import BytesIO
from langchain_together import ChatTogether
from basic_tools import DateTool, TimeTool
from dotenv import load_dotenv
import base64
import streamlit as st
from PIL import Image
from langchain.schema import HumanMessage
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)
st_callback = StreamlitCallbackHandler(st.container())

load_dotenv()

# Debug print
print(f"Current working directory: {os.getcwd()}")
print(f"TOGETHER_AI_API_KEY set: {'Yes' if os.getenv('TOGETHER_AI_API_KEY') else 'No'}")

# Initialize Chat Model
try:
    model = ChatTogether(
        together_api_key=os.getenv("TOGETHER_AI_API_KEY2"),
        # model="meta-llama/Llama-Vision-Free",
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        temperature=0
    )
    print("Model initialized successfully")
except Exception as e:
    print(f"Error initializing model: {str(e)}")
    sys.exit(1)


# Streamlit Interface
st.title("Multimodal Chat")

# Allow users to upload an image
uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
content = []
# Handle both text and image inputs
if uploaded_image:
    for img in uploaded_image:
        image = Image.open(img)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        # Pass the image to the agent as input

# Handle text input
if prompt := st.chat_input("Enter your message"):
    st.chat_message("user").write(prompt)

    content.append({"type": "text", "text": prompt})
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        if uploaded_image:
            for img in uploaded_image:
                buffered = BytesIO()
                image = Image.open(img)
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"},
                })

        message = HumanMessage(content)
        # Invoke the agent with the image and prompt
        response = model.invoke(
            [message], {"callbacks": [st_callback]}
        )
        # Display the response
        st.write(response.content)
