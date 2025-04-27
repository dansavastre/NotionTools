import requests, json
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NOTION_API_KEY")
databaseID = os.getenv("DATABASE_ID")
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_page(database_id, data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": database_id}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    # print(res.status_code)
    return res

def get_pages(database_id, num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # Comment this out to dump all data to a file
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)
    
    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


def get_page_blocks(page_id):
    """
    Fetch all blocks (content) from a Notion page.
    """
    url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page blocks: {response.text}")
    data = response.json()
    return data.get("results", [])
    

def get_block_children(block_id, page_size=100):
    """
    Fetch all children of a Notion block.
    """

    url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size={page_size}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch block children: {response.text}")
    
    data = response.json()
    return data.get("results", [])






def get_block_tree(block_id, page_size=100):
    """
    """
    children = get_block_children(block_id)

    for child in children:
        if child["has_children"]:
            child["children"] = get_block_tree(child["id"])
        else:
            child["children"] = []

    return children

def get_all_page_content(page_id):
    blocks = get_page_blocks(page_id)
    for block in blocks:
        if block.get("has_children", False):
            block["children"] = get_block_tree(block["id"])
        else:
            block["children"] = []
    return blocks


# ------------------------------ Notion2Anki ------------------------------

import json

def block_to_html(block, indent=""):
    """
    Convert a Notion block (and its children) to pretty-printed HTML with text styling.
    """
    block_html = ""
    
    def apply_styles(text, styles):
        """Apply styles like bold, italics, underline to the text."""
        if not text:
            return text
        
        if "bold" in styles and styles["bold"]:
            text = f"<b>{text}</b>"
        if "italic" in styles and styles["italic"]:
            text = f"<i>{text}</i>"
        if "strikethrough" in styles and styles["strikethrough"]:
            text = f"<s>{text}</s>"
        if "underline" in styles and styles["underline"]:
            text = f"<u>{text}</u>"
        
        return text
    
    # Check the type of block and generate HTML accordingly
    if block["type"] == "paragraph":
        block_html = indent + "<p>"
        if "rich_text" in block["paragraph"]:
            for text_obj in block["paragraph"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</p>\n"
        
    elif block["type"] == "heading_1":
        block_html = indent + "<h1>"
        if "rich_text" in block["heading_1"]:
            for text_obj in block["heading_1"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</h1>\n"
        
    elif block["type"] == "heading_2":
        block_html = indent + "<h2>"
        if "rich_text" in block["heading_2"]:
            for text_obj in block["heading_2"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</h2>\n"
        
    elif block["type"] == "heading_3":
        block_html = indent + "<h3>"
        if "rich_text" in block["heading_3"]:
            for text_obj in block["heading_3"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</h3>\n"
        
    elif block["type"] == "bulleted_list_item":
        block_html = indent + "<ul>\n"  # Open the <ul> here
        block_html += indent + "  <li>"
        if "rich_text" in block["bulleted_list_item"]:
            for text_obj in block["bulleted_list_item"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</li>\n"  # Close <li> after text content
        for child in block.get("children", []):
            block_html += (block_to_html(child, indent + "  ")) + "\n"
        block_html += indent + "</ul>\n"  # Close the <ul> at the end
        
    elif block["type"] == "numbered_list_item":
        block_html = indent + "<ol>\n"  # Open the <ol> here
        block_html += indent + "  <li>"
        if "rich_text" in block["numbered_list_item"]:
            for text_obj in block["numbered_list_item"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</li>\n"  # Close <li> after text content
        for child in block.get("children", []):
            block_html += block_to_html(child, indent + "  ") + "\n"
        block_html += indent + "</ol>\n"  # Close the <ol> at the end
        
    elif block["type"] == "to_do":
        block_html = indent + "<ul>\n"  # Open the <ul> here
        block_html += indent + "  <li>"
        if "rich_text" in block["to_do"]:
            for text_obj in block["to_do"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        if "children" in block["to_do"]:
            for child in block["to_do"]["children"]:
                block_html += block_to_html(child, indent + "  ") + "\n"
        block_html += "</li>\n"  # Close <li> after text content
        block_html += indent + "</ul>\n"  # Close the <ul> at the end
        
    elif block["type"] == "toggle":
        block_html = indent + "<details><summary>"
        if "rich_text" in block["toggle"]:
            for text_obj in block["toggle"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        block_html += "</summary>\n"
        for child in block.get("children", []):
            block_html += block_to_html(child, indent + "  ") + "\n"
        block_html += indent + "</details>\n"
        
    elif block["type"] == "quote":
        block_html = indent + "<blockquote>"
        if "rich_text" in block["quote"]:
            for text_obj in block["quote"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        for child in block.get("children", []):
            block_html += block_to_html(child, indent + "  ") + "\n"
        block_html += "</blockquote>\n"
        
    elif block["type"] == "callout":
        block_html = indent + "<div class='callout'>"
        if "rich_text" in block["callout"]:
            for text_obj in block["callout"]["rich_text"]:
                text = text_obj.get("plain_text", "")
                styles = text_obj.get("annotations", {})
                block_html += apply_styles(text, styles)
        if "icon" in block["callout"]:
            icon = block["callout"]["icon"].get("emoji", "")
            block_html += f"<span class='icon'>{icon}</span>"
        for child in block.get("children", []):
            block_html += block_to_html(child, indent + "  ")
        block_html += "</div>\n"
        
    elif block["type"] == "image":
        block_html = indent + "<img src='" + (block["image"]["file"]["url"] if "file" in block["image"] else block["image"]["external"]["url"]) + "' alt='Image' />\n"

    return block_html
