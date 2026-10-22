
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-6-luna")
parser = StrOutputParser()


def split_transcript(transcript: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200,
    )

    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    # Step 1: Summarize each text chunk
    map_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Summarize this portion of a meeting transcript concisely. "
            "Preserve important decisions, action items, names, and key details."
        ),
        ("human", "{text}"),
    ])

    map_chain = map_prompt | llm | parser

    chunks = split_transcript(transcript)

    if not chunks:
        return ""

    chunk_summaries = [
        map_chain.invoke({"text": chunk})
        for chunk in chunks
    ]

    # Step 2: Combine partial summaries
    combined = "\n\n".join(chunk_summaries)

    combined_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert meeting summarizer. "
            "Combine these partial summaries into one professional "
            "meeting summary. Use clear bullet points. "
            "Preserve decisions, action items, and important details."
        ),
        ("human", "{text}"),
    ])

    combined_chain = combined_prompt | llm | parser

    return combined_chain.invoke({"text": combined})


def generate_title(transcript: str) -> str:
    title_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Generate a short, professional title for this meeting. "
            "Use no more than 8 words. Return only the title."
        ),
        ("human", "{text}"),
    ])

    title_chain = title_prompt | llm | parser

    return title_chain.invoke({"text": transcript[:2000]}).strip()
