from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from functions import read_file


def ask_ai(job_txt):
    llm = ChatOpenAI(model="gpt-4o-mini")

    user_skills = read_file("prompt.txt")

    prompt_template = user_skills + "\n\n" + "{job}"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                'Eres un asistente que se encarga de evaluar si un trabajo se adecua a los requerimientos, tu respuesta (en minuscula) es la clasificacion del trabajo (una de dos opciones) "relevante" o "no-relevante". Si no sabes si es relevante o no, contesta con "relevante"',
            ),
            ("user", prompt_template),
        ]
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"job": job_txt})
    return response
