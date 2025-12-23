import os
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class TransactionResponse(BaseModel):
    descricao_limpa: str = Field(description="Nome simplificado e legível do estabelecimento ou serviço.")
    categoria: str = Field(description="A categoria financeira mais adequada para este gasto.")

CATEGORIAS_PERMITIDAS = [
    "Alimentação", "Transporte", "Lazer", "Saúde", 
    "Educação", "Moradia", "Assinaturas", "Outros"
]

def classificar_transacao(descricao_bruta: str) -> TransactionResponse:
    # --- DIRETRIZES DE DESEMPATE ---
    # Isso remove a dúvida da IA em casos como o "Bar do Zé"
    diretrizes = """
    REGRAS DE HIERARQUIA:
    1. Locais focados em entretenimento noturno, bebidas ou socialização (Bares, Pubs, Quiosques) -> Sempre 'Lazer'.
    2. Estabelecimentos focados em refeições (Restaurantes, Fast-food, Padarias) -> Sempre 'Alimentação'.
    3. Lojas dentro de postos de combustível -> Sempre 'Transporte'.
    4. Serviços recorrentes de tecnologia -> Sempre 'Assinaturas'.
    5. Serviços como academia ou farmácias ou relacionados à atividades físicas -> Sempre 'Saúde'.
    6. Serviços públicos como água, luz, gás -> Sempre 'Moradia'.
    7. Se a transação não se encaixar claramente em nenhuma categoria, use 'Outros'.
    8. Priorize categorias específicas sobre genéricas (ex: 'Lazer' sobre 'Outros').
    9. Em casos de dúvida entre duas categorias, escolha a que for mais específica para o contexto do gasto.
    """

    # --- EXEMPLOS FEW-SHOT ATUALIZADOS ---
    exemplos = """
    Exemplos para seguir:
    - Entrada: 'PG *IFOOD.COM BR' -> Saída: {"descricao_limpa": "iFood", "categoria": "Alimentação"}
    - Entrada: 'BAR DO ZE - SAO PAULO' -> Saída: {"descricao_limpa": "Bar do Zé", "categoria": "Lazer"}
    - Entrada: 'UBER *TRIP' -> Saída: {"descricao_limpa": "Uber", "categoria": "Transporte"}
    - Entrada: 'NETFLIX.COM' -> Saída: {"descricao_limpa": "Netflix", "categoria": "Assinaturas"}
    - Entrada: 'DROGASIL' -> Saída: {"descricao_limpa": "Drogasil", "categoria": "Saúde"}
    - Entrada: 'SABESP' -> Saída: {"descricao_limpa": "Sabesp", "categoria": "Moradia"}
    """

    prompt_sistema = f"""
    Você é um assistente financeiro de alta precisão.
    Sua tarefa é limpar nomes de transações e categorizá-las corretamente.
    
    Categorias permitidas: {", ".join(CATEGORIAS_PERMITIDAS)}
    
    {diretrizes}
    
    Regras gerais:
    1. Sempre use o singular para as categorias (ex: 'Transporte').
    2. Remova códigos, datas e símbolos.
    3. Se não houver categoria clara, use 'Outros'.
    
    {exemplos}
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Classifique esta transação: {descricao_bruta}"}
        ],
        response_format=TransactionResponse,
        temperature=0 # <--- Define como zero para garantir que a resposta seja sempre a mesma (determinística)
    )

    return response.choices[0].message.parsed