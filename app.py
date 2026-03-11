import streamlit as st

# 1. Title and Header
st.title("My First Streamlit App")
st.write("Hello, World!")

# 2. Create a Button
if st.button('Click Me!'):
    # This code runs only when the button is pressed
    st.balloons()  # A fun animation
    st.success("You clicked the button! The app is working.")
else:
    st.info("Wait for it... click the button above.")
