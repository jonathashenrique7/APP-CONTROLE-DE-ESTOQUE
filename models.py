from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend import Base # Atualizado o nome do import

class Categoria(Base):
    __tablename__ = "categorias" # Correção: __tablename__
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True)
    produtos = relationship("Produto", back_populates="categoria", cascade="all, delete")

class Produto(Base):
    __tablename__ = "produtos" # Correção: __tablename__
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    quantidade = Column(Integer)
    preco = Column(Float)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    categoria = relationship("Categoria", back_populates="produtos")