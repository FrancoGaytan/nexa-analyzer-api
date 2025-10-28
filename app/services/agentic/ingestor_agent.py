import os
import pdfplumber
from docx import Document
import requests
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

class IngestorAgent:
    def __init__(self, name="ingestor", api_key: str = None, system_message: str = None):
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment or passed explicitly.")

        if system_message is None:
            system_message = (
                "You are the Ingestor agent. Your job is to read and process client-provided materials, such as RFPs, briefing documents, or public information, in PDF, DOCX, TXT, or from URLs. "
                "You must extract and normalize all text content, preserving as much structure as possible (e.g., section headers, bullet points), and generate metadata including page numbers, anchors, and source references. "
                "Return a dictionary with two keys: 'text_blocks' (a list of normalized text blocks with their anchors) and 'metadata' (including file type, page numbers, and any other relevant info). "
                "Do not summarize or interpret content; only extract and structure it for downstream processing."
            )

        self.model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)
        self.agent = AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    def ingest(self, file_path: str = None, url: str = None):
        """
        Ingests a document (PDF, DOCX, TXT) or a URL and returns normalized text blocks and metadata.
        Returns:
            dict: { 'text_blocks': [ { 'text': ..., 'anchor': ... } ], 'metadata': { ... } }
        """
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                return self._ingest_pdf(file_path)
            elif ext in (".docx", ".doc"):
                return self._ingest_docx(file_path)
            elif ext == ".txt":
                return self._ingest_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        elif url:
            return self._ingest_url(url)
        else:
            raise ValueError("Either file_path or url must be provided.")

    def _ingest_pdf(self, file_path):
        text_blocks = []
        metadata = {"file_type": "pdf", "pages": []}
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                anchor = f"page_{i}"
                text_blocks.append({"text": text, "anchor": anchor})
                metadata["pages"].append({"page": i, "anchor": anchor})
        return {"text_blocks": text_blocks, "metadata": metadata}

    def _ingest_docx(self, file_path):
        doc = Document(file_path)
        text_blocks = []
        metadata = {"file_type": "docx", "paragraphs": []}
        for i, para in enumerate(doc.paragraphs, 1):
            text = para.text.strip()
            if text:
                anchor = f"para_{i}"
                text_blocks.append({"text": text, "anchor": anchor})
                metadata["paragraphs"].append({"index": i, "anchor": anchor})
        return {"text_blocks": text_blocks, "metadata": metadata}

    def _ingest_txt(self, file_path):
        text_blocks = []
        metadata = {"file_type": "txt"}
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, 1):
            text = line.strip()
            if text:
                anchor = f"line_{i}"
                text_blocks.append({"text": text, "anchor": anchor})
        metadata["lines"] = len(text_blocks)
        return {"text_blocks": text_blocks, "metadata": metadata}

    def _ingest_url(self, url):
        resp = requests.get(url)
        resp.raise_for_status()
        text = resp.text
        text_blocks = []
        for i, para in enumerate(text.split("\n\n"), 1):
            para = para.strip()
            if para:
                anchor = f"block_{i}"
                text_blocks.append({"text": para, "anchor": anchor})
        metadata = {"file_type": "url", "url": url, "blocks": len(text_blocks)}
        return {"text_blocks": text_blocks, "metadata": metadata}
