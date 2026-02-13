import os  # <-- ADICIONADO: Necessário para manipular pastas
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backup import realizar_backup 
import models, backend 

# Inicialização do Banco de Dados
models.Base.metadata.create_all(bind=backend.engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Injeção de Dependência do Banco
def get_db():
    db = backend.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- EVENTOS DE CICLO DE VIDA ---

@app.on_event("startup")
def startup_event():
    """Roda ao ligar o servidor"""
    if not os.path.exists("backups"):
        os.makedirs("backups")
    print("\n" + "="*30)
    print("🚀 SISTEMA DE ESTOQUE ONLINE")
    print("📂 Pasta de backups verificada.")
    print("="*30 + "\n")

@app.on_event("shutdown")
def shutdown_event():
    """Roda ao desligar (Ctrl + C)"""
    print("\n" + "!"*30)
    print("💾 Iniciando backup de segurança...")
    realizar_backup()
    print("👋 Servidor encerrado com sucesso.")
    print("!"*30 + "\n")

# --- ROTAS DO SISTEMA ---

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_produtos = db.query(models.Produto).count()
    return templates.TemplateResponse("index.html", {"request": request, "total": total_produtos})

@app.post("/produtos/atualizar/{id}")
def atualizar_estoque(id: int, nova_qtd: int = Form(...), db: Session = Depends(get_db)):
    prod = db.query(models.Produto).filter(models.Produto.id == id).first()
    if prod:
        prod.quantidade = nova_qtd
        db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/categorias")
def listar_categorias(request: Request, db: Session = Depends(get_db)):
    cats = db.query(models.Categoria).all()
    return templates.TemplateResponse("categorias.html", {"request": request, "categorias": cats})

@app.post("/categorias/nova")
def criar_categoria(nome: str = Form(...), db: Session = Depends(get_db)):
    nova_cat = models.Categoria(nome=nome)
    db.add(nova_cat)
    db.commit()
    return RedirectResponse(url="/categorias", status_code=303)

@app.get("/categorias/deletar/{id}")
def deletar_categoria(id: int, db: Session = Depends(get_db)):
    cat = db.query(models.Categoria).filter(models.Categoria.id == id).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse(url="/categorias", status_code=303)

@app.get("/produtos")
def listar_produtos(request: Request, db: Session = Depends(get_db)):
    prods = db.query(models.Produto).all()
    cats = db.query(models.Categoria).all()
    return templates.TemplateResponse("produtos.html", {"request": request, "produtos": prods, "categorias": cats})

@app.post("/produtos/novo")
def criar_produto(nome: str = Form(...), qtd: int = Form(...), preco: float = Form(...), cat_id: int = Form(...), db: Session = Depends(get_db)):
    novo_prod = models.Produto(nome=nome, quantidade=qtd, preco=preco, categoria_id=cat_id)
    db.add(novo_prod)
    db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/produtos/deletar/{id}")
def deletar_produto(id: int, db: Session = Depends(get_db)):
    prod = db.query(models.Produto).filter(models.Produto.id == id).first()
    if prod:
        db.delete(prod)
        db.commit()
    return RedirectResponse(url="/produtos", status_code=303)

@app.get("/graficos")
def exibir_graficos(request: Request, db: Session = Depends(get_db)):
    produtos = db.query(models.Produto).all()
    labels = [p.nome for p in produtos]
    valores = [p.quantidade for p in produtos]
    return templates.TemplateResponse("graficos.html", {"request": request, "labels": labels, "valores": valores})