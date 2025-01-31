import azure.functions as func
import logging
import re
import json


app =func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
# Configuration du logger optimisée pour Azure Functions
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def detect_type_examen( titre):
        def normalize_type(text):
              replacements = {
                  r'acromioclaviculaire': "ACROMIOCLAVICULAIRE (RADIOGRAPHIE DE L'ARTICULATION ACROMIO-CLAVICULAIRE)",
                  r'pangonogramme': "PANGONOGRAMME (RADIOGRAPHIE DES DENTS)",
                  r'asp': "ASP (RADIOGRAPHIE DE L'ABDOMEN SANS PRÉPARATION)",
                  r'urocanner': "UROSCANNER (SCANNER DES REINS)",
                  r'arm': "ARM (IRM DES VAISSEAUX SANGUINS)",
                  r'bili irm': "BILI IRM (IRM DES VOIES BILIAIRES)",
                  r'entero irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                  r'entéro irm': "ENTERO IRM (IRM DE L'INTESTIN)",
                  r'angio irm': "ENGIO IRM (IRM ANGIOGRAPHIQUE DES VAISEAUX SANGUINS)",
                  r'uroscanner': "UROSCANNER (SCANNER DES VOIES URINAIRES)",
                  r'dacryoscanner': "DACRYOSCANNER (SCANNER DES VOIES LACRYMALES)",
                  r'coroscanner': "COROSCANNER (SCANNER DES ARTERES DU COEUR)",
                  r'entéroscanner': "ENTEROSCANNER (SCANNER DU L'INTESTIN)",
                  r'coloscanner': "COLOSCANNER (SCANNER DU COLON)",
                  r'arthro-scanner': "ARTHRO-SCANNER (SCANNER DES ARTICULATIONS )",
                  r'arthro-irm': "ARTHRO-IRM (IRM DES ARTICULATIONS )",
                  r'ostéodensitométrie': "OSTÉODENSITOMÉTRIE (RADIOGRAPHIE DES OS )",
                  r'cystographie': "CYSTOGRAPHIE (RADIOGRAPHIE DE LA VESSIE )",
                  r'discographie': "DISCOGRAPHIE (RADIOGRAPHIE DE DISQUE INTERVERTÉBRAL )",
                  r'togd': "TOGD (RADIOGRAPHIE DE L'\u0152SOPHAGE ET DE L'ESTOMAC )",
                  r'urographie': "UROGRAPHIE (RADIOGRAPHIEE DES VOIES URINAIRES )",
                  r'hystérographie': "HYSTÉROGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE )",
                  r'hystérosalpingographie': "HYSTÉROSALPINGOGRAPHIE (RADIOGRAPHIE DE LA CAVITÉ UTÉRINE )",
                  r'cone beam': "CONE BEAM (RADIOGRAPHIE DES DENTS)",
                  r'tomographie': "TOMOGRAPHIE (RADIOGRAPHIE DES DENTS)",
                  r'doppler': "DOPPLER (ECHOGRAPHIE DES VAISSEAUX)",
              }
              for pattern, replacement in replacements.items():
                        text = re.sub(pattern, replacement,text, flags=re.IGNORECASE)
              return text

        keywords = {
                "RADIO": ["radio", "radiographie", "x-ray", "rayon x"],
                "SCANNER": ["scanner", "tdm", "tomodensitométri", "scan"],
                "IRM": ["irm", "imagerie par résonance magnétique"],
                "ECHOGRAPHIE": ["echo", "écho", "échographie", "echographie", "ultrason", "ultrasound",'échotomographie','ultrasonore'],
                "Mammographie": ["mammographie", "mammogramme", "mammo", "mamographie", "examen du sein", "imagerie mammaire"]
            }
        titre_lower = normalize_type(titre.lower()).lower()
        for category, words in keywords.items():
                if any(word in titre_lower for word in words):
                    return category

        return "AUTRE"


@app.route(route="detect_exam")
def detect_exam(req: func.HttpRequest) -> func.HttpResponse:
    """Gère la requête en fonction du texte reçu"""
    logger.info("Début du traitement de la requête HTTP")
    try:
        req_body = req.get_json()
        logger.info("Corps de la requête JSON récupéré avec succès")
    except ValueError:
        logger.error("Erreur lors de la récupération du corps de la requête. Le JSON est invalide.")
        return func.HttpResponse("Invalid JSON", status_code=400)

    texte = req_body.get("texte", "").strip()

    # Vérification des paramètres
    if not texte:
        logger.warning("Paramètre 'texte' manquant ou invalide.")
        return func.HttpResponse("Le paramètre 'texte' est requis", status_code=400)
    logger.info(f"Texte reçu : {texte[:50]}...")  # Affichage limité pour ne pas exposer de données sensibles dans les logs

    # Exécution de la fonction de détection de type d'examen
    try:
        result = detect_type_examen(texte)
        logger.info(f"Résultat de la détection : {result}")
        return func.HttpResponse(json.dumps({"type_examen": result}), mimetype="application/json", status_code=200)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du type d'examen : {str(e)}")
        return func.HttpResponse(f"Erreur lors de l'extraction : {str(e)}", status_code=500)

       
           
