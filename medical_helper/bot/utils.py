import os

from langchain_community.document_loaders import PyMuPDFLoader


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def remove_ws(d):
    text = d.page_content.replace('\n', ' ')
    d.page_content = text
    return d


def load_multiple(file_paths: list[str]):
    all_pages = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        if file_path.endswith('.pdf'):
            loader = PyMuPDFLoader(file_path)
        else:
            print(f"Unsupported file type: {file_path}")
            continue

        pages = loader.load()
        all_pages.extend(pages)

    return all_pages
