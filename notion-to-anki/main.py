import streamlit as st

html_content = """
<ul>
    <li>Pellicle formation
        <ul><li>(minuten tot uren, mn eiwitten uit speeksel)</li></ul>
    </li>
    <li>Early colonizers
        <ul><li>bacteriën worden aangetrokken door van der Waals krachten en binden aan eiwitten op de pellicle</li></ul>
    </li>
    <li>co-adhesion and growth of attached bacteria
        <ul><li>na 8 uur, binnen 24 uur 1e laag</li></ul>
        <ul><li>niet uniform</li></ul>
        <ul><li>milieu verandering geschikt voor andere bacteriën</li></ul>
    </li>
    <li>microbial succession
        <ul><li>24 uur tot 1 week</li></ul>
        <ul><li>groei via celdeling</li></ul>
        <ul><li>aanmaak van EPS voor biofilm matrix</li></ul>
    </li>
    <li>climax community
        <ul><li>facultatief obligate anaeroob</li></ul>
        <ul><li>met O2 gradatie</li></ul>
        <ul><li>pH verandert</li></ul>
        <ul><li>buitenste laag is lossig</li></ul>
        <ul><li>binnenste laag is stevig</li></ul>
    </li>
</ul>
"""

# Render the HTML in Streamlit
st.markdown(html_content, unsafe_allow_html=True)


# from dotenv import load_dotenv
# import sys
# import os
# from services.notion_client import get_pages

# load_dotenv()
# databaseID = os.getenv("NOTION_DATABASE_ID")

# if __name__ == "__main__":
#     pages = get_pages(databaseID, num_pages=5)
#     print(f"Fetched {len(pages)} pages")

#     for i, page in enumerate(pages):
#         page_id = page.get("id")
#         props = page.get("properties", {})
#         title_prop = next((v for v in props.values() if v.get("type") == "title"), None)

#         title = ""
#         if title_prop and title_prop["title"]:
#             title = title_prop["title"][0]["plain_text"]

#         print(f"{i+1}. Page ID: {page_id}, Title: {title}")

