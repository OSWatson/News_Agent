# test_regulations_tool.py

from tools.regulations import search_regulations, get_document_details

def main():
    print("\n🔍 Searching regulations for 'cryptocurrency'...\n")
    results = search_regulations("cryptocurrency", max_results=100)

    print(f"✅ Found {len(results)} documents.\n")

    for i, doc in enumerate(results[:10]):  # Show first 10
        title = doc['attributes'].get('title', 'No title')
        doc_id = doc['id']
        posted = doc['attributes'].get('postedDate', 'Unknown date')
        print(f"{i+1}. {title}\n   ID: {doc_id}\n   Posted: {posted}\n")

    if results:
        first_id = results[0]['id']
        print(f"\n📄 Fetching details for document ID: {first_id}...\n")
        detail = get_document_details(first_id)

        title = detail['data']['attributes'].get('title')
        summary = detail['data']['attributes'].get('abstractText', 'No summary available.')
        print(f"Title   : {title}")
        print(f"Summary : {summary[:500]}...")  # Trim long summaries

if __name__ == "__main__":
    main()
