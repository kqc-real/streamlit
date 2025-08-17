import streamlit as st

def start_mc_test():
	user_id_input = st.session_state.get('user_id_input', '').strip()
	if not user_id_input:
		st.sidebar.error("Bitte ein Pseudonym eingeben.")
	else:
		st.session_state.user_id = user_id_input
		st.rerun()

st.sidebar.text_input(
	"Pseudonym eingeben (frei wählbar)",
	key='user_id_input',
	on_change=start_mc_test
)
