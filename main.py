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

# Usiamo il modello Flash più recente e stabile
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- SICUREZZA ---
def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "money2025" 
    
    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Accesso Negato.",
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
    mode: str = Form(...),            
    product_name: str = Form(...), 
    features: str = Form(...), 
    target: str = Form(...),          
    tone: str = Form(...),
    language: str = Form(...),        # NUOVO: Lingua Output
    extra_opt: bool = Form(False),    
    auth: bool = Depends(check_credentials)
):
    
    # Istruzioni Social/Extra migliorate
    social_section = ""
    if extra_opt:
        if mode == "real_estate":
            social_section = f"""
            ---
            ### 📱 SOCIAL MEDIA KIT (Instagram/Facebook)
            **Caption:** Scrivi una caption breve, accattivante e formattata con spaziature.
            **Hashtag:** Inserisci 15 hashtag strategici per {target}.
            """
        else:
            social_section = """
            ---
            ### 📧 EMAIL RECUPERO CARRELLO
            **Oggetto:** Un oggetto che garantisce il 60% di open rate.
            **Corpo:** Un testo persuasivo che usa la leva della scarsità.
            """

    # Prompt Dinamici
    if mode == "real_estate":
        prompt = f"""
        Ruolo: Copywriter Immobiliare Senior di fama mondiale.
        Lingua Output: {language}
        
        INPUT:
        - Immobile: {product_name}
        - Dettagli Tecnici: {features}
        - Zona/Target: {target}
        - Tono di voce: {tone}
        
        COMPITO:
        Scrivi un annuncio immobiliare strutturato in Markdown.
        1. **Headline** (H1): Magnetica, specifica.
        2. **Storytelling**: Descrivi l'esperienza di vita, non solo i muri.
        3. **Caratteristiche Premium**: Bullet points.
        4. **Zona**: Perché viverci è comodo/bello.
        5. **CTA**: Urgente ma elegante.
        
        {social_section}
        """

    else: # E-commerce
        prompt = f"""
        Ruolo: Esperto SEO e Conversion Copywriter per E-commerce top 1%.
        Lingua Output: {language}
        
        INPUT:
        - Prodotto: {product_name}
        - Specifiche: {features}
        - Keywords/Target: {target}
        - Tono: {tone}
        
        COMPITO:
        Scrivi una scheda prodotto strutturata in Markdown.
        1. **Titolo SEO** (H1): Include keywords, max 120 caratteri.
        2. **Hook**: Le prime 2 righe devono catturare l'attenzione.
        3. **Descrizione Emozionale**: Usa la tecnica "Benefit over Features".
        4. **Bullet Points**: 5 motivi per acquistare ORA.
        5. **Specifiche Tecniche**: Tabella pulita.
        6. **FAQ**: 3 domande e risposte per abbattere obiezioni.
        
        {social_section}
        """
    
    try:
        response = await model.generate_content_async(prompt)
        return JSONResponse(content={"result": response.text, "status": "success"})
    except Exception as e:
        return JSONResponse(content={"result": f"Errore API: {str(e)}", "status": "error"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)