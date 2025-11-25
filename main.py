import os
import secrets
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import google.generativeai as genai
import uvicorn
from dotenv import load_dotenv

# --- CONFIGURAZIONE ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("Nessuna API KEY trovata. Crea il file .env!")

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SISTEMA DI SICUREZZA (SAAS MODEL) ---
def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    # ⚠️ CAMBIA QUESTE CREDENZIALI PRIMA DI DARE IL SITO AI CLIENTI!
    correct_username = "admin"
    correct_password = "money2025" 
    
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accesso Negato: Paga l'abbonamento per entrare.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# --- ROTTE ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, auth: bool = Depends(check_credentials)):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate")
async def generate_desc(
    request: Request,
    mode: str = Form(...),            # real_estate o ecommerce
    product_name: str = Form(...), 
    features: str = Form(...), 
    target: str = Form(...),          # Zona (Real Estate) o Keywords (Ecom)
    tone: str = Form(...),
    extra_opt: bool = Form(False),    # Social (Real Estate) o Email (Ecom)
    auth: bool = Depends(check_credentials)
):
    
    # SELEZIONE DEL "CERVELLO" (PROMPT)
    if mode == "real_estate":
        # --- MODALITÀ IMMOBILIARE ---
        extra_instruction = ""
        if extra_opt:
            extra_instruction = """
            AGGIUNTA SOCIAL:
            Alla fine, crea un post Instagram/Facebook breve e coinvolgente con 10 hashtag mirati per il settore immobiliare.
            """
            
        prompt = f"""
        Agisci come un Copywriter Immobiliare Senior di lusso.
        DATI:
        - Immobile: {product_name}
        - Dettagli: {features}
        - Zona: {target}
        - Tono: {tone}
        
        OUTPUT RICHIESTO (Markdown):
        1. H1: Titolo magnetico (non usare "Vendesi").
        2. Intro emozionale (storytelling).
        3. Lista puntata caratteristiche premium.
        4. Descrizione della zona e servizi.
        5. CTA (Call to Action) urgente.
        {extra_instruction}
        """

    else:
        # --- MODALITÀ E-COMMERCE (Shopify/Amazon) ---
        extra_instruction = ""
        if extra_opt:
            extra_instruction = """
            BONUS RECUPERO CARRELLO:
            Alla fine, scrivi una Email Oggetto + Corpo per un cliente che ha abbandonato questo prodotto nel carrello. Usa psicologia della scarsità e offri un piccolo incentivo.
            """

        prompt = f"""
        Agisci come un Esperto SEO e Copywriter per E-commerce (Amazon/Shopify).
        DATI PRODOTTO:
        - Nome: {product_name}
        - Specifiche/Materiali: {features}
        - Keywords SEO / Target: {target}
        - Tono: {tone}
        
        OUTPUT RICHIESTO (Markdown):
        1. **Titolo Ottimizzato SEO** (Include le keyword principali, max 150 caratteri).
        2. **Descrizione Persuasiva** (Usa la tecnica AIDA: Attenzione, Interesse, Desiderio, Azione).
        3. **5 Bullet Points** "Perché comprarlo" (Focus sui benefici, non solo caratteristiche).
        4. **Specifiche Tecniche** (Tabella o lista pulita).
        5. **Sezione FAQ** (Genera 3 domande frequenti e rispondi per abbattere le obiezioni).
        {extra_instruction}
        """
    
    try:
        response = await model.generate_content_async(prompt)
        return JSONResponse(content={"result": response.text, "status": "success"})
    except Exception as e:
        return JSONResponse(content={"result": f"Errore API: {str(e)}", "status": "error"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)