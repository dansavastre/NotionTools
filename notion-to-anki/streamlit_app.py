import streamlit as st
import os
import services.notion_client as nc
import services.anki_client as ac
import html

st.title("🧠 Notion2Anki")

# notionKey = os.getenv("NOTION_API_KEY")
# databaseID = os.getenv("NOTION_DATABASE_ID")

# Function to process toggle blocks into question-answer pairs
def process_toggle_block(block):
    question = block["toggle"]["rich_text"][0]["plain_text"] if block["toggle"]["rich_text"] else "No Question"
    answer = ""
    for child in block["children"]:
        answer += (nc.block_to_html(child) + "\n")  # Process children into HTML
    return {"question": question, "answer": answer}


def show_pages():
    """Fetch and display pages from Notion."""

    if notionKey is None or databaseID is None:
        st.error("Missing NOTION_API_KEY or DATABASE_ID in your environment.")
    else:
        notion_client = nc.NotionClient(notionKey)
        pages = notion_client.get_pages(databaseID)
        st.success(f"Fetched {len(pages)} pages from Notion!")

        for page in pages:
            props = page.get("properties", {})
            title_prop = next((v for v in props.values() if v.get("type") == "title"), None)

            title = "(No Title)"
            if title_prop and title_prop["title"]:
                title = title_prop["title"][0]["plain_text"]
            
            with st.expander(title):
                # st.json(page)
            
                if st.button(f"Generate flashcards for {title}"):
                    blocks = notion_client.get_all_page_content(page["id"])
                    # st.success(f"Loaded {len(blocks)} top-level blocks!")

                    # st.json(blocks)

                    flashcards = []

                    # Process toggle blocks and create flashcards
                    for block in blocks:
                        if block["type"] == "toggle":
                            flashcards.append(process_toggle_block(block))

                    # Display flashcards in a nice format
                    for idx, flashcard in enumerate(flashcards):
                        st.markdown(f"### Flashcard {idx + 1}")
                        st.text_area("Question:", flashcard['question'], height=100)
                        st.text_area("Answer:", flashcard['answer'], height=200)

                        existing_notes = []
                        if title not in ac.get_deck_names():
                            result = ac.create_deck(title)
                            if result.get("error") is None:
                                st.success(f"Deck '{title}' created successfully!")
                            else:
                                st.error(f"Error creating deck: {result['error']}")
                            existing_notes = ac.get_notes(title)
                        
                        # for note in existing_notes:
                        #     note['fields']['Front'] = html.unescape(note['fields']['Front'])
                        #     note['fields']['Back'] = html.unescape(note['fields']['Back'])
                        if flashcard['question'] in [note['fields']['Front'] for note in existing_notes]:
                            st.warning(f"Flashcard already exists in the deck '{title}'!")
                        else:
                            result = ac.add_note(title, flashcard['question'], flashcard['answer'])
                            if result.get("error") is None:
                                st.success(f"Note added successfully!")
                            else:
                                st.error(f"Error adding note: {result['error']}")
                        

if __name__ == "__main__":
    # Ask the user to input their API key and Database ID
    notionKey = st.text_input("Enter your Notion API Key")
    databaseID = st.text_input("Enter your Notion Database ID")

    if notionKey and databaseID:
        # Store values in session state for later use
        st.session_state.notionKey = notionKey
        st.session_state.databaseID = databaseID

        # Proceed with your app logic
        st.write("Thank you! You're now connected.")
        show_pages()
    else:
        st.write("Please enter your credentials to connect.")