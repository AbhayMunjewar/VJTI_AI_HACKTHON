import streamlit as st
from llm.nl_query import process_natural_language_query

def render_ai_assistant_page(df_filtered):
    st.markdown("### 💬 Natural Language AI Decision Assistant")
    st.markdown("Ask natural language questions about state HTE data, instantly compute statistics, and render dynamic visualizations.")

    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Suggested Prompts (Clickable Chips)
    st.markdown("##### 💡 Suggested Demo Questions (Click to Ask):")
    chip_cols = st.columns(3)

    sample_questions = [
        "Which districts have the highest dropout rate in engineering?",
        "Show enrollment trend for CS departments across all districts",
        "Which institutes have placement rates above 80%?",
        "Compare total state funding allocations between Pune and Mumbai",
        "What is the relationship between student faculty ratio and placement percentage?"
    ]

    selected_prompt = None

    with chip_cols[0]:
        if st.button(f"📌 {sample_questions[0]}", key="chip_0", use_container_width=True):
            selected_prompt = sample_questions[0]
        if st.button(f"📌 {sample_questions[3]}", key="chip_3", use_container_width=True):
            selected_prompt = sample_questions[3]

    with chip_cols[1]:
        if st.button(f"📌 {sample_questions[1]}", key="chip_1", use_container_width=True):
            selected_prompt = sample_questions[1]
        if st.button(f"📌 {sample_questions[4]}", key="chip_4", use_container_width=True):
            selected_prompt = sample_questions[4]

    with chip_cols[2]:
        if st.button(f"📌 {sample_questions[2]}", key="chip_2", use_container_width=True):
            selected_prompt = sample_questions[2]

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat Input Box
    user_input = st.chat_input("Type your question here... (e.g. 'Which department has highest package in Pune?')")

    active_query = selected_prompt or user_input

    if active_query:
        # Add user question to history
        st.session_state.chat_history.append({"role": "user", "content": active_query})

        with st.spinner("Processing natural language query & generating visual..."):
            result = process_natural_language_query(active_query, df_filtered)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer_text"],
            "fig": result.get("fig"),
            "table": result.get("table")
        })

    # Render Chat History
    for idx, msg in enumerate(reversed(st.session_state.chat_history[-8:])):
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("fig") is not None:
                    st.plotly_chart(msg["fig"], use_container_width=True, key=f"chat_fig_{idx}")
                if msg.get("table") is not None and not msg["table"].empty:
                    with st.expander("🔍 View Data Table Details"):
                        st.dataframe(msg["table"], use_container_width=True)

    # Clear Chat Button
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Conversation History"):
            st.session_state.chat_history = []
            st.rerun()
