from pathlib import Path
import streamlit.components.v1 as components

_drag = components.declare_component('task1_drag_board',path=str(Path(__file__).parent/'drag_frontend'))


def drag_board(cards, boxes, initial, key, mode):
    return _drag(cards=[{'id':c['id'],'text':c['text']} for c in cards],
                 boxes=boxes,initial=initial,mode=mode,default=initial,key=key)
