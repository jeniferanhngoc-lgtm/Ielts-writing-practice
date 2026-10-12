"""Render answers as prose, never Streamlit's implicit JSON renderer."""
import streamlit as st


def readable_text(value):
    if isinstance(value,dict):
        return '\n'.join(f'{key}: {readable_text(item)}' for key,item in value.items())
    if isinstance(value,(list,tuple)):
        return '\n'.join(readable_text(item) for item in value)
    return str(value)


def show_answer(value, order_options=None):
    if order_options and isinstance(value,list):
        for alternative in value:
            ids=alternative if isinstance(alternative,list) else [alternative]
            for i,ident in enumerate(ids,1):
                try:
                    text=order_options[int(ident)-1]
                except (ValueError,IndexError,TypeError):
                    text=str(ident)
                st.write(f'{i}. {text}')
        return
    if isinstance(value,dict):
        for key,item in value.items():
            st.markdown(f'**{key}**')
            show_answer(item)
    elif isinstance(value,(list,tuple)):
        for item in value:
            if isinstance(item,(list,tuple)):
                st.write(' → '.join(str(x) for x in item))
            else:
                st.write(str(item))
    else:
        st.write(str(value))
