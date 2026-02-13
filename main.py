from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models, backend # Atualizado: de database para backend

# Atualizado: backend.engine
models.Base.metadata.create_all(bind=backend.engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = backend.SessionLocal() # Atualizado: backend.SessionLocal
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_produtos = db.query(models.Produto).count()
    return templates.TemplateResponse("index.html", {"request": request, "total": total_produtos})

@app.post("/produtos/atualizar/{id}")
def atualizar_estoque(id: int, nova_qtd: int = Form(...), db: Session = Depends(get_db)):
    # Busca o produto no banco pelo ID
    prod = db.query(models.Produto).filter(models.Produto.id == id).first()
    
    if prod:
        prod.quantidade = nova_qtd  # Atualiza o valor
        db.commit()                 # Salva no banco
        
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