import streamlit as st
import pandas as pd
import time
import pickle
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer
from streamlit_folium import st_folium
import folium
from underthesea import word_tokenize

# import the model
df = pickle.load(open('C:/Users/TechCare/Documents/df.pkl','rb'))
df_des=pickle.load(open('C:/Users/TechCare/Documents/df_des.pkl','rb'))
#
def recommendations(des, DEST):

    recommended_hotels = []
    links=[]
    addresses =[]
    scores =[]
    descriptions=[]
    lat = []
    lon = []

    
    ks = pd.DataFrame({'links':['1'],'names':['ABC'],'reviews':['1'],'scores':['1'],
                      'addresses': ['1'],'Description':['1'],'latitude_longitude': ['1'],'DEST': ['1'],'descriptions_clean':[des],'lat':['1'],'lon':['1']})
    
    
    hotel = df[df.DEST == DEST]
    hotel = pd.concat([ks, hotel], ignore_index = True)
    
    
    #tính tf-idf + cosine_similarities
    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 4), min_df=0)
    tfidf_matrix = tf.fit_transform(hotel['descriptions_clean'])
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
    #chuyển names thành index
    hotel.set_index('names', inplace = True)
    indices = pd.Series(hotel.index)
    # gettin the index of the hotel that matches the name
    idx = indices[indices == 'ABC'].index[0]
    # creating a Series with the similarity scores in descending order
    score_series = pd.Series(cosine_similarities[idx]).sort_values(ascending = False)

    # getting the indexes of the 10 most similar hotels except itself
    top_10_indexes = list(score_series[score_series>0].index[1:11])
    
    # populating the list with the names of the top 10 matching hotels
    for i in top_10_indexes:
        recommended_hotels.append(list(hotel.index)[i])
        links.append(list(hotel['links'])[i])
        addresses.append(list(hotel['addresses'])[i])
        scores.append(list(hotel['scores'])[i])
        descriptions.append(list(hotel['descriptions'])[i])
        lat.append(list(hotel['lat'])[i])
        lon.append(list(hotel['lon'])[i])
  
    return pd.DataFrame({'links':links,'names':recommended_hotels,'addresses': addresses,'scores':scores,'Description':descriptions,'lat': lat,'lon': lon})
#GIAO DIỆN APP
st.set_page_config(
    page_title="RECOMMEND SYSTEM",
    page_icon="🔥",
    layout="wide"
)

#GIAO DIỆN
st.title('👉🏼HOTEL RECOMMEND SYSTEM👈🏼')
with st.form("Thông tin"):
    name = st.text_input('👉🏽Nhập vào mô tả khách sạn',value='Bạn muốn: ')
    location = st.selectbox('👉🏽Tỉnh/thành phố',
                              ['Đà Lạt', 'Hà Nội', 'TP. Hồ Chí Minh', 'Vũng Tàu', 'Đà Nẵng', 'Phú Quốc', 'Hội An', 'Nha Trang', 'Sa Pa', 'Huế'])
    location_name=location
    st.write('**👉🏽Bạn muốn tìm khách sạn có mô tả như sau:**', name)
    st.write('**👉🏽Ở tỉnh/ thành phố:**', location_name)
    submit = st.form_submit_button("Xác nhận")
    dest_name = ['Đà Lạt', 'Hà Nội', 'TP. Hồ Chí Minh', 'Vũng Tàu', 'Đà Nẵng', 'Phú Quốc', 'Hội An', 'Nha Trang', 'Sa Pa', 'Huế']
    dest_id = [-3712045, -3714993, -3730078, -3733750, -3712125, -3726177, -3715584, -3723998, -3728113, -3715887]
    for i in range(len(dest_name)):
        if location == dest_name[i]:
            location = dest_id[i]
###########################################
name = word_tokenize(name,format = 'text')
#Nút tìm kiếm
deploy = st.button('Tìm kiếm')
if deploy:
    with st.spinner("đang chạy..."):
        time.sleep(1)
    try:
        
        a=recommendations(name, location)
        # tạo map
        with st.form('Map'):
            b=a[['lat','lon']]
            locationlist = b.values.tolist()
            map = folium.Map(location=[locationlist[0][0], locationlist[0][1]], zoom_start=14)
            for point in range(0, len(locationlist)):
                folium.Marker(locationlist[point],
                              popup='◀️Score▶️ '+str(a.iloc[point,3]) + ' ◀️Name▶️ '+str(a.iloc[point,1])+' ◀️Address▶️ '+str(a.iloc[point,2])).add_to(map)
            st_data = st_folium(map, width =1500,height=500)
            submit = st.form_submit_button('MAP',disabled=True)
        #
        st.success('Tìm kiếm thành công', icon="✅")
        st.write('**Dưới đây là những khách sạn tương tự với mô tả của bạn ở**',location_name)
        for i in range(len(a)):
            with st.form(''+str(i)+''):
                st.markdown(f'**👀Name Hotel**: {a.iloc[i,1]}')
                st.markdown(f'**👀Address**: {a.iloc[i,2]}')
                st.markdown(f'**👀Score**: {a.iloc[i,3]}🔴')
                st.markdown(f'**👀Description**: {a.iloc[i,4][:1500]}...')
                st.markdown(f'[Go to Website]({a.iloc[i,0]})')
                submit = st.form_submit_button(str(i+1),disabled=True)              
    except:
        st.error('Không tìm thấy khách sạn tương tự '+name+' ở '+location_name+' hoặc không tồn tại khách sạn giống với mô tả '+name, icon="❌")
########################################################
def main():
    with st.sidebar:
        st.button(
            "hiển thị những tiện ích ở "+location_name,
            on_click=location_form )
#st.markdown('Place: ',df_des[df_des.iloc[i,0]==location].iloc[i,2])
def location_form():
    with st.sidebar:
        with st.form('more infor'):
            for i in range(len(df_des)):
                if df_des.iloc[i,0] == location:
                    st.markdown(f'Place:\n {df_des.iloc[i,2]}')
                    st.markdown(f'Food:\n {df_des.iloc[i,3]}')
            submit = st.form_submit_button('đóng')     

if __name__ == "__main__":
    main()
#Đặt ảnh nền############################################################################
import base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("D:/pythonProject/image4.jpg")


page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://cf.bstatic.com/images/hotel/max1024x768/378/378828506.jpg");
background-size: 100%;
background-position: center;
background-repeat: repeat;
background-attachment: local;
}}
[data-testid="stSidebar"] > div:first-child {{
background-image: url("data:image/png;base64,{img}");
background-position: center; 
background-repeat: repeat;
background-attachment: fixed;
}}
[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}
[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)


#
