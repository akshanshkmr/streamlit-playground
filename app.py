import streamlit as st
from streamlit_ace import st_ace

_app_title = 'Streamlit Playground'

def security_check(code):
    import re
    restricted_modules = ['os','sys','pathlib']
    for module in restricted_modules:
        if re.search("import.*" + module, code) or re.search("from.*" + module, code):
            raise ImportError(module)
    return True

if __name__ == '__main__':
    st.set_page_config(
        page_title=_app_title,
        layout='wide',
        page_icon='🚀')

    st.title(_app_title)

    if 'code' in st.session_state.keys():
        code = st.session_state['code']
        if st.button('Back to Editor 📝'):
            st.session_state['code_bk'] = code
            st.session_state.pop('code')
            st.experimental_rerun()

        if security_check(code):
            st.write('Running Code:')
            st.code(code)
            st.write('Output:')
            exec(code)
    else:
        with st.form(key='editor'):
            if 'code_bk' in st.session_state.keys():
                code = st_ace(
                    theme='dracula',
                    auto_update=True,
                    language='python',
                    height=600,
                    font_size=16,
                    value=st.session_state['code_bk'])
            else:
                code = st_ace(
                    theme='dracula',
                    auto_update=True,
                    language='python',
                    height=600,
                    font_size=18)
            if st.form_submit_button('Run 🏃‍♂️') and security_check(code):
                st.session_state['code'] = code
                st.experimental_rerun()
