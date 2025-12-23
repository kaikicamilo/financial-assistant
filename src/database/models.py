import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "financeiro.db")

# 1. Configuração Inicial
Base = declarative_base()
# O SQLite criará um arquivo chamado 'financeiro.db' na sua pasta
engine = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=engine)

# 2. Definição das Tabelas
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # Relacionamentos (ajuda o SQLAlchemy a buscar dados ligados ao usuário)
    transactions = relationship("Transaction", back_populates="user")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(20)) # 'receita', 'despesa' ou 'investimento'
    
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    valor = Column(Float, nullable=False)
    data = Column(DateTime, default=datetime.utcnow)
    
    # Campos pensados para sua IA
    descricao_bruta = Column(String(255)) # Ex: "PG *IFOOD_123"
    descricao_limpa = Column(String(255)) # Ex: "iFood"
    
    # Campo JSON para guardar dados extras do OCR (Task 11)
    metadata_ia = Column(JSON, nullable=True) 
    
    # Chaves Estrangeiras (Relacionamentos)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

class Budget(Base):
    __tablename__ = 'budgets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    valor_limite = Column(Float, nullable=False)
    mes_ano = Column(String(7)) # Formato "MM/AAAA"

# 3. Criação das tabelas no arquivo .db
def init_db():
    Base.metadata.create_all(engine)
    print("Banco de dados e tabelas criados com sucesso!")

if __name__ == "__main__":
    init_db()