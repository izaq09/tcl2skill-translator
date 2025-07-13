import json
import streamlit as st

from translator import translate_tcl_code_to_skill_code

# Set page layout to wide
st.set_page_config(layout="wide")

# Define API list
with open("data/syntax_reference_api.json", "r") as f:
    api_list = list(json.load(f).keys())


def extract_api_calls(tcl_code, api_list):
    found, not_found = [], []
    for api in api_list:
        if api in tcl_code:
            found.append(api)
        else:
            not_found.append(api)
    return found, not_found


# Layout: two columns
left, right = st.columns([1, 2])

with left:
    st.header("Upload TCL File")
    uploaded_file = st.file_uploader("Choose a TCL file", type=["tcl"])
    tcl_code = ""
    if uploaded_file is not None:
        tcl_code = uploaded_file.read().decode("utf-8")

with right:
    st.header("TCL Source Code")
    if tcl_code:
        st.code(tcl_code, language="tcl")
    else:
        st.info("No TCL file uploaded.")

    st.header("API Presence Check")
    if tcl_code:
        apis_found, apis_not_found = extract_api_calls(
            tcl_code=tcl_code, api_list=api_list
        )
        markdown_str = ""
        if apis_found:
            markdown_str += "".join(
                [":green-badge[{}]".format(api) for api in apis_found]
            )

        if apis_not_found:
            markdown_str += "".join(
                [":gray-badge[{}]".format(api) for api in apis_not_found]
            )

        st.markdown(markdown_str)
    else:
        st.write("Upload a file to see APIs.")

    st.header("Translated SKILL Code")
    if tcl_code:
        skill_code = translate_tcl_code_to_skill_code(tcl_code=tcl_code)
        st.code(skill_code, language="c")
    else:
        st.info("Upload a file to see translation.")
