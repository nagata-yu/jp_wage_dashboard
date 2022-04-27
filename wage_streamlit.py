import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px


st.title('日本の賃金データダッシュボード')

df_jp_ind = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv', encoding='shift_jis')
df_jp_category = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv', encoding='shift_jis')
df_pref_ind = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv', encoding='shift_jis')


# 都道府県別一人あたり平均賃金を日本地図にヒートマップ表示する
st.header('2019年：一人当たり平均賃金のヒートマップ')
# 県庁所在地の緯度経度情報
jp_lat_lon = pd.read_csv('./code_file/pref_lat_lon.csv')
# データフレームのカラム名変更
jp_lat_lon = jp_lat_lon.rename(columns={'pref_name': '都道府県名'})
# 条件で抽出する
df_pref_map = df_pref_ind[(df_pref_ind['年齢'] == '年齢計') & (df_pref_ind['集計年'] == 2019)]
# 緯度経度情報と結合する
df_pref_map = pd.merge(df_pref_map, jp_lat_lon, on='都道府県名')
# 一人当たり賃金の数値を正規化する
df_pref_map['一人当たり賃金（相対値）'] = ((df_pref_map['一人当たり賃金（万円）'] - df_pref_map['一人当たり賃金（万円）'].min()) / (df_pref_map['一人当たり賃金（万円）'].max() - df_pref_map['一人当たり賃金（万円）'].min()))

# pydeckの設定
# ヒートマップの中心地を指示 → 例として東京の座標値
view = pdk.ViewState(
    longitude=139.691649,
    latitude=35.689185,
    zoom=4,
    pitch=40.5,
)
# レイヤーの設定
layer = pdk.Layer(
    'HeatmapLayer',
    data=df_pref_map,
    opacity=0.4,
    get_position=['lon', 'lat'],
    threshold=0.3,
    get_weight='一人当たり賃金（相対値）'
)
# レンダリング
layer_map = pdk.Deck(
    layers=layer,
    initial_view_state=view,
)
# ヒートマップ表示
st.pydeck_chart(layer_map)
# チェックボックスでデータフレーム表示/非表示
show_df = st.checkbox('Show DataFrame')
if show_df == True:
    st.write(df_pref_map)


# 集計年別の一人あたり平均賃金の推移グラフ
st.header('集計年別の一人当たり賃金（万円）の推移')
# 全国一人当たり賃金に対して条件抽出したデータフレームを作成
df_ts_mean = df_jp_ind[(df_jp_ind['年齢'] == '年齢計')]
# データフレームのカラム名変更
df_ts_mean = df_ts_mean.rename(columns={'一人当たり賃金（万円）': '全国_一人当たり賃金（万円）'})
# 都道府県別一人当たり賃金に対して条件抽出したデータフレームを作成
df_pref_mean = df_pref_ind[(df_pref_ind['年齢'] == '年齢計')]
# 都道府県のユニークな値をリストとして抽出する
pref_list = df_pref_mean['都道府県名'].unique()
# セレクトボックスにリストの項目を入れる
option_pref = st.selectbox(
    '都道府県名',
    (pref_list)
)
# 選択された都道府県名で条件抽出を行う
df_pref_mean = df_pref_mean[df_pref_mean['都道府県名'] == option_pref]
# セレクトボックスに連動するデータフレームを表示
df_pref_mean
# df_ts_mean と df_pref_meanを集計年で結合する
df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on='集計年')
# 必要な列だけに絞る
df_mean_line = df_mean_line[['集計年', '全国_一人当たり賃金（万円）', '一人当たり賃金（万円）']]
# 集計年をインデックスに変える
df_mean_line = df_mean_line.set_index('集計年')
# 上記データをもとに折れ線グラフ作成
st.line_chart(df_mean_line)


# 年齢階級別の一人当たり平均賃金（万円）をバブルチャートで可視化
st.header('年齢階級別の一人当たり平均賃金（万円）')
# 年齢計に絞って条件抽出
df_mean_bubble = df_jp_ind[df_jp_ind['年齢'] != '年齢計']
# plotly expressの設定
fig = px.scatter(df_mean_bubble, 
                 x='一人当たり賃金（万円）', 
                 y='年間賞与その他特別給与額（万円）', 
                 range_x=[150, 700], 
                 range_y=[0, 150], 
                 size='所定内給与額（万円）', 
                 size_max=38, #バブルサイズのMAXのこと
                 color='年齢', 
                 animation_frame='集計年', 
                 animation_group='年齢'
)
# streamlitからplotlyを呼び出す
st.plotly_chart(fig)


# 産業別の平均賃金を横棒グラフ表示
st.header('産業別の賃金推移')
# 集計年のユニークな値をリスト化して代入する
year_list = df_jp_category['集計年'].unique()
# セレクトボックスにリストの項目を入れる
option_year = st.selectbox(
    '集計年', 
    (year_list)
)
# 賃金の種類をリスト化する
wage_list = ['一人当たり賃金（万円）', '所定内給与額（万円）', '年間賞与その他特別給与額（万円）']
# セレクトボックスにリストの項目を入れる
option_wage = st.selectbox(
    '賃金の種類',
    (wage_list)
)
# セレクトボックスで選択した集計年で条件抽出する設定
df_mean_categ = df_jp_category[(df_jp_category['集計年'] == option_year)]
# 賃金の種類によって最大値を取得する + マージンを設定
max_x = df_mean_categ[option_wage].max() + 50
# plotly expressの設定
fig = px.bar(df_mean_categ, 
             x=option_wage, 
             y='産業大分類名', 
             color='産業大分類名', 
             animation_frame='年齢', 
             range_x=[0,max_x], 
             orientation='h',  #横棒グラフ表示にする為、'h'になる
             width=800, 
             height=500
)
# streamlitからplotlyを呼び出す
st.plotly_chart(fig)


# オープンソースデータの出展もとを必ず記載する
st.text('出典：RESAS （地域経済分析システム）')
st.text('本結果はRESAS（地域経済分析システム）を加工して作成')