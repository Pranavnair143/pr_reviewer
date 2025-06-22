import streamlit as st

from agents.reviewer.graph import initialize_graph
from utils.pr_info_extractor import extract_azure_pr_info


st.title("Azure PR Reviewer")

# Input Fields
pr_link = st.text_input("🔗 Pull Request Link", type="password", placeholder="https://dev.azure.com/<organization>/<project_name>/_git/<repository>/pullrequest/<pr_id>")
personal_access_token = st.text_input("🔐 Personal Access Token", type="password")
code_option = st.radio("🧠 Code Extraction Mode", ["Full code", "Only code changes"])

# Validation and Execution
if st.button("🚀 Run"):
    errors = []
    if not pr_link.strip():
        errors.append("Pull Request Link is required.")
    if not personal_access_token.strip():
        errors.append("Personal Access Token is required.")
    if code_option not in ["Full code", "Only code changes"]:
        errors.append("Please select a valid Code Extraction Mode.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        # Assemble Info Dictionary
        info = {
            "pr_link": pr_link,
            "personal_access_token": personal_access_token,
            "full_code": code_option == "Full code"
        }

        try:
            # Extract Azure PR Info
            pr_details = extract_azure_pr_info(pr_link)
            info.update(pr_details)

            # Initialize and Invoke Graph
            graph = initialize_graph(info=info)
            initial_state = {"messages": []}
            final_state = graph.invoke(initial_state)

            # Display Output
            if final_state["messages"]:
                last_message = final_state["messages"][-1]
                st.success("✅ Final Message:")
                st.write(last_message.content)
            else:
                st.warning("⚠️ No messages found in final state.")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")