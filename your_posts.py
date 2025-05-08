import streamlit as st
from firebase_admin import firestore
import pandas as pd
  
def app():
    st.title('Bills of: '+st.session_state['username'] )
    try:
        if 'db' not in st.session_state:
            st.session_state.db = ''

        db=firestore.client()
        st.session_state.db=db

        docs =db.collection('Bills').document(st.session_state['username']).get()

        d=docs.to_dict()
        data = []
        for i in d['Content']:
            try:
                new_row = {
                    'Merchant Name': i['Merchant Name'],
                    'Total_price': i['Total_price'],
                    'Date': i['Date']
                }
                data.append(new_row)
            except KeyError as e:
                st.error(f'Missing key in bill data: {e}')
                return

        df = pd.DataFrame(data)
        st.dataframe(df,hide_index=True)
        st.line_chart(df,x='Date',y='Total_price')
        # df=pd.DataFrame()
        # for i in d['Content']:
        #     new_row = ['Date'=i['Date'],
        #                'Merchant Name'=i['Merchant Name'],
        #                'Total_price'=i['Total_price']]
        #     df=df.append(new_row,ignore_index=True)
        # st.dataframe(df)


        # df=pd.DataFrame(d)
        # st.dataframe(df)


        # st.write(d)
        # st.write(docs)

            
        # result = db.child('Users').child(st.session_state['username']).get()
        # r=result.to_dict()
        # content = r['Content']
        # st.write('Bills:')
        
        # def delete_bill(k):
        #     c=int(k)
        #     h=content[c]
        #     try:
        #         db.child('Users').child(st.session_state['username']).update({
        #                         "Merchant Name": '',
        #                         "Total_price": '',
        #                         "Date": ''
        #                     })
        #         st.warning('Bill deleted')
        #     except:
        #         st.write('Something went wrong..')
                
        # for c in range(len(content)-1,-1,-1):
        #     st.text_area(label='',value=content[c])
        #     st.button('Delete Bill', on_click=delete_bill, args=([c] ), key=c)        

        
    except:
        if st.session_state.username=='':
            st.text('Please Login first')        
