import streamlit as st
from openai import OpenAI
import pyperclip

# Page configuration with custom theme
st.set_page_config(
    page_title="AI Prompt Optimizer",
    page_icon="🎯",
    layout="wide",
)

# Custom CSS for better UI
st.markdown("""
    <style>
        .stTextArea textarea {
            font-family: monospace;
        }
        .stButton button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def optimize_prompt(task_or_prompt):
    META_PROMPT = """
        Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively. The prompt must be in the same language as the one you are given.

        # Guidelines

        - Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
        - Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
        - Reasoning Before Conclusions**: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
        - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
        - Conclusion, classifications, or results should ALWAYS appear last.
        - Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
        - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
        - Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
        - Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
        - Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
        - Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
        - Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
        - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias towards outputting a JSON.
        - JSON should never be wrapped in code blocks (```) unless explicitly requested.

        The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

        [Concise instruction describing the task - this should be the first line in the prompt, no section header]

        [Additional details as needed.]

        [Optional sections with headings or bullet points for detailed steps.]

        # Steps [optional]

        [optional: a detailed breakdown of the steps necessary to accomplish the task]

        # Output format

        [Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

        # Examples [optional]

        [Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
        [If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

        # Notes [optional]

        [optional: edge cases, details, and an area to call or repeat out specific important considerations]
    """.strip()

    client = OpenAI(api_key=st.secrets['OPENAI_KEY'])
    try:
        with st.spinner("🤔 Ottimizzazione in corso..."):
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": META_PROMPT},
                    {"role": "user", "content": f"Task, Goal, or Current Prompt:\n{task_or_prompt}"},
                ]
            )
            return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Errore durante l'ottimizzazione del prompt: {str(e)}")
        return None

# Initialize session state for the optimized prompt
if "optimized_prompt" not in st.session_state:
    st.session_state.optimized_prompt = ""


col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Prompt")
    user_input = st.text_area(
        "Inserisci qui il tuo prompt o la descrizione del task",
        height=300,
        placeholder="Es: Scrivi un'email di follow-up per un cliente potenziale...",
        key="input_area"
    )
    
    col1_1, col1_2, col1_3 = st.columns([1, 2, 1])
    
    with col1_2:
        optimize_button = st.button(
            "✨ Ottimizza Prompt",
            use_container_width=True,
            disabled=not bool(user_input.strip())
        )
    with col1_3:
        if st.button("🔄 Ricomincia", use_container_width=True):
            st.session_state.optimized_prompt = ""
            user_input = ""
            st.rerun()

with col2:
    st.subheader("Prompt Ottimizzato")
    output_container = st.container(border=True)
    
    if optimize_button and user_input:
        optimized_prompt = optimize_prompt(user_input)
        if optimized_prompt:
            st.session_state.optimized_prompt = optimized_prompt
            
    if st.session_state.optimized_prompt:
        with output_container:
            st.markdown(st.session_state.optimized_prompt)
            
            if st.button("📋 Copia negli Appunti", use_container_width=True):
                pyperclip.copy(st.session_state.optimized_prompt)
                st.write("Copiato negli appunti!")