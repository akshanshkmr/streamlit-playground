import io
import re
import textwrap
import contextlib

import streamlit as st
from streamlit_ace import st_ace

_app_title = 'Streamlit Playground 🛝'
_sample_snippet = textwrap.dedent(
    """
    # Try editing this snippet
    import streamlit as st
    import numpy as np
    import pandas as pd

    st.title("Random line chart")

    data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=["A", "B", "C"],
    )

    st.line_chart(data)
    """
)


def security_check(code: str) -> bool:
    """Block obviously dangerous imports before execution."""
    restricted_modules = ['os', 'sys', 'pathlib']
    for module in restricted_modules:
        if re.search(rf"(^|\\n)\\s*(import|from)\\s+{module}\\b", code):
            raise ImportError(module)
    return True


def run_code(code: str) -> tuple[str, str]:
    """Execute user code while capturing stdout/stderr."""
    stdout_buffer, stderr_buffer = io.StringIO(), io.StringIO()
    exec_globals: dict[str, object] = {}
    with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(
        stderr_buffer
    ):
        exec(code, exec_globals)
    return stdout_buffer.getvalue(), stderr_buffer.getvalue()


if __name__ == '__main__':
    st.set_page_config(
        page_title=_app_title,
        layout='wide',
        page_icon='🚀',
    )

    st.title(_app_title)

    with st.sidebar:
        st.subheader('How to use')
        st.markdown(
            '- Edit code in the editor\n'
            '- Press **Run** to execute safely\n'
            '- Use **Back to Editor** to make changes'
        )
        if st.button('Insert sample snippet', use_container_width=True):
            st.session_state['code_bk'] = _sample_snippet
            st.session_state.pop('code', None)
            st.rerun()
        st.link_button(
            'Request new library ➕',
            'https://github.com/akshanshkmr/streamlit-playground/edit/main/requirements.txt',
            type='secondary',
            use_container_width=True,
            help='Opens requirements.txt to propose a new dependency',
        )

    if 'code' in st.session_state:
        code = st.session_state['code']
        top_bar = st.columns([5, 1])
        with top_bar[0]:
            st.subheader('Run')
        with top_bar[1]:
            if st.button('Back to Editor 📝', type='secondary', use_container_width=True):
                st.session_state['code_bk'] = code
                st.session_state.pop('code', None)
                st.rerun()

        with st.expander('View code', expanded=False):
            st.code(code, language='python')

        output_col, console_col = st.columns([3, 1])
        with output_col:
            st.subheader('Streamlit output')
            streamlit_slot = st.container()

        with console_col:
            st.subheader('Console')
            stdout_slot = st.container()

        try:
            if security_check(code):
                with st.spinner('Running...'):
                    # render user Streamlit output inside a scoped container
                    with streamlit_slot:
                        stdout, stderr = run_code(code)

                with stdout_slot:
                    if stdout:
                        st.code(stdout)
                    else:
                        st.info('No stdout.')

        except Exception as exc:  # noqa: BLE001 broad for UX
            st.error(f'Execution stopped: {exc}')
    else:
        with st.form(key='editor'):
            st.caption('Tip: try the sample snippet in the sidebar.')
            ace_kwargs = dict(
                theme='terminal',
                auto_update=True,
                language='python',
                height=600,
            )
            if 'code_bk' in st.session_state:
                ace_kwargs['value'] = st.session_state['code_bk']
                ace_kwargs['font_size'] = 16
            else:
                ace_kwargs['font_size'] = 18

            code = st_ace(**ace_kwargs)
            submitted = st.form_submit_button('Run 🏃‍♂️', use_container_width=True)
            if submitted:
                try:
                    if security_check(code):
                        st.session_state['code'] = code
                        st.rerun()
                except Exception as exc:  # noqa: BLE001
                    st.error(f'Security check failed: {exc}')
