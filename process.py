import streamlit as st
from firebase_admin import firestore

def app(data):
    if 'db' not in st.session_state:
        st.session_state.db = ''

    db=firestore.client()
    st.session_state.db=db

    if data!='':
        info = db.collection('Bills').document(st.session_state.username).get()
        if info.exists:
            info = info.to_dict()
            if 'Content' in info.keys():
            
                pos=db.collection('Bills').document(st.session_state.username)
                pos.update({u'Content': firestore.ArrayUnion([data])})
                # st.success('Post uploaded!!')
            else:
                data={"Content":[data],'Username':st.session_state.username}
                db.collection('Bills').document(st.session_state.username).set(data)    
        else:
                
            data={"Content":[data],'Username':st.session_state.username}
            db.collection('Bills').document(st.session_state.username).set(data)
            
