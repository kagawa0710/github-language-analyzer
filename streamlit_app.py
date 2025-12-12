import requests
import streamlit as st
import pandas as pd
import re

def parse_github_url(url):
    """GitHubのURLからowner/repoを抽出"""
    # https://github.com/owner/repo の形式
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, url)
    if match:
        owner = match.group(1)
        repo = match.group(2).rstrip('/')
        # .gitを削除
        repo = repo.replace('.git', '')
        return owner, repo
    return None, None

def get_github_languages(owner, repo):
    """GitHubリポジトリの言語情報を取得"""
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def display_language_stats(owner, repo, top_n=5):
    """言語統計を綺麗に表示"""
    languages = get_github_languages(owner, repo)
    
    if not languages:
        st.error("❌ データを取得できませんでした。リポジトリ名を確認してください。")
        return
    
    # 合計バイト数を計算
    total = sum(languages.values())
    
    # パーセンテージを計算してソート
    lang_percentages = [
        {
            "Language": lang,
            "Percentage": (bytes_count / total) * 100,
            "Bytes": bytes_count
        }
        for lang, bytes_count in languages.items()
    ]
    lang_percentages.sort(key=lambda x: x["Percentage"], reverse=True)
    
    # 上位N件を表示
    top_languages = lang_percentages[:top_n]
    
    # リポジトリ情報
    st.success(f"✅ **Repository:** [{owner}/{repo}](https://github.com/{owner}/{repo})")
    
    # タイトル
    st.subheader(f"📊 Languages Distribution (Top {len(top_languages)})")
    
    # プログレスバーで表示
    for lang_data in top_languages:
        lang = lang_data["Language"]
        percentage = lang_data["Percentage"]
        
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(percentage / 100, text=f"**{lang}**")
        with col2:
            st.metric("", f"{percentage:.1f}%", label_visibility="collapsed")
    
    # バーチャート
    st.subheader("📈 Chart View")
    df_chart = pd.DataFrame(top_languages).set_index("Language")["Percentage"]
    st.bar_chart(df_chart, height=300)
    
    # 詳細テーブル
    with st.expander("📋 View Details"):
        df = pd.DataFrame(lang_percentages)[["Language", "Percentage", "Bytes"]]
        df["Percentage"] = df["Percentage"].apply(lambda x: f"{x:.2f}%")
        df["Bytes"] = df["Bytes"].apply(lambda x: f"{x:,}")
        st.dataframe(df, hide_index=True, use_container_width=True)

# メインアプリ
st.set_page_config(page_title="GitHub Language Analyzer", page_icon="📊", layout="wide")

st.title("📊 GitHub Repository Language Analyzer")
st.markdown("GitHubリポジトリの言語構成を分析・可視化します")

# URL入力
github_url = st.text_input(
    "🔗 GitHub Repository URL",
    value="https://github.com/streamlit/streamlit",
    placeholder="https://github.com/owner/repository",
    help="GitHubリポジトリのURLを入力してください"
)

# URL解析
owner, repo = parse_github_url(github_url)

if owner and repo:
    st.info(f"📦 Analyzing: **{owner}/{repo}**")
    
    # 自動で分析を実行
    with st.spinner("🔍 データ取得中..."):
        display_language_stats(owner, repo, top_n=5)
else:
    st.warning("⚠️ 有効なGitHubリポジトリURLを入力してください")
    st.markdown("**例:** `https://github.com/streamlit/streamlit`")