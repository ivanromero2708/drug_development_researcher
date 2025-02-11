import asyncio
import httpx
import logging
import re
import requests
import pubchempy as pcp
from typing import Optional, Dict, List
from pydantic import BaseModel
from src.literature_research_agent.state import LiteratureResearchGraphState

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

# Modelo de datos para la salida (sin valores default problemáticos)
class APIExternalData(BaseModel):
    cas_number: Optional[str] = None
    description: Optional[str] = None
    solubility: Optional[str] = None
    melting_point: Optional[str] = None
    chemical_names: Optional[str] = None
    molecular_formula: Optional[str] = None
    molecular_weight: Optional[float] = None
    log_p: Optional[str] = None
    boiling_point: Optional[str] = None

class SearchExternalAPIs:
    CHEMBL_API_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"
    PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.client = httpx.AsyncClient(headers={"Content-Type": "application/json"})
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def fetch(self, url: str) -> Optional[Dict]:
        """
        Realiza una solicitud HTTP GET con reintentos en caso de error.
        """
        for attempt in range(self.max_retries):
            try:
                response = await self.client.get(url, timeout=10)
                response.raise_for_status()
                return response.json() if response.text.strip() else None
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error for {url}: {e}")
            except httpx.RequestError as e:
                logging.error(f"Request error for {url}: {e}")
            await asyncio.sleep(self.retry_delay)
        return None

    def get_chembl_data(self, name: str) -> Optional[Dict]:
        """
        Obtiene información de la API de CHEMBL por nombre del compuesto.
        """
        url = f"{self.CHEMBL_API_BASE_URL}/molecule/search?q={name}&format=json"
        try:
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=10)
            response.raise_for_status()
            return response.json() if response.text.strip() else None
        except requests.RequestException as e:
            logging.error(f"Error in get_chembl_data: {e}")
            return None

    def get_cid(self, inchikey: str) -> Optional[str]:
        """
        Obtiene el CID de PubChem basado en el InChIKey.
        """
        try:
            compounds = pcp.get_compounds(inchikey, namespace="inchikey")
            return compounds[0].cid if compounds else None
        except Exception as e:
            logging.error(f"Error in get_cid: {e}")
            return None

    def get_cas(self, smiles: str) -> str:
        """
        Obtiene el número CAS basado en la estructura SMILES.
        """
        try:
            compounds = pcp.get_compounds(smiles, "smiles")
            if compounds and compounds[0].synonyms:
                for syn in compounds[0].synonyms:
                    if "-" in syn and syn.replace("-", "").isdigit():
                        return syn
            return "No disponible"
        except Exception as e:
            logging.error(f"Error in get_cas: {e}")
            return "Error"

    async def get_specific_properties(self, cid: str) -> Dict[str, List[str]]:
        """
        Obtiene propiedades específicas del compuesto en PubChem.
        """
        endpoints = {
            "Physical Description": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=physical+description",
            "Dissociation Constants": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Dissociation+Constants",
            "LogP": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=LogP",
            "Solubility": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=solubility",
            "Melting Point": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Melting+Point",
            "Boiling Point": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Boiling+Point",
            "Molecular Formula": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Molecular+Formula",
            "IUPAC Name": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=IUPAC+Name",
        }
        tasks = [self.fetch(url) for url in endpoints.values()]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        data = {}
        for key, response in zip(endpoints.keys(), responses):
            if isinstance(response, dict):
                data[key] = self.extract_property(response)
            else:
                logging.error(f"Error fetching {key}: {response}")
                data[key] = []
        return data

    def extract_property(self, response: Dict) -> List[str]:
        """
        Extrae información relevante de un JSON de respuesta.
        """
        results = []
        def recursive_search(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "String" and isinstance(v, str):
                        results.append(v)
                    else:
                        recursive_search(v)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_search(item)
        recursive_search(response)
        return results

    async def search_external_apis(self, state: LiteratureResearchGraphState):
        """
        Ejecuta la búsqueda de información en ChEMBL y PubChem.
        """
        api_name = state["API"].API_name
        chembl_json = self.get_chembl_data(api_name)
        if not chembl_json or "molecules" not in chembl_json or not chembl_json["molecules"]:
            logging.error(f"No se encontraron datos en ChEMBL para '{api_name}'.")
            return {"api_external_APIkey_data": None}

        molecule = chembl_json["molecules"][0]
        molecule_structures = molecule.get("molecule_structures", {})
        smiles = molecule_structures.get("canonical_smiles", "NA")
        InChiKey = molecule_structures.get("standard_inchi_key", "NA")
        cas_number = self.get_cas(smiles)
        cid = self.get_cid(InChiKey)
        
        # Obtener peso molecular usando PubChem
        compounds = pcp.get_compounds(InChiKey, "inchikey")
        if compounds:
            compound = compounds[0]
            molecular_weight = getattr(compound, "molecular_weight", None)
        else:
            molecular_weight = None

        specific_properties = await self.get_specific_properties(cid)

        # Función para extraer temperaturas de manera segura
        def extract_temp(prop_list: List[str]) -> str:
            for point in prop_list:
                if re.search(r"\d+ °C", point):
                    return point
            return prop_list[0] if prop_list else "Información no disponible"

        # Función para extraer el primer valor de forma segura
        def extract_first(prop_list: List[str]) -> str:
            return prop_list[0] if prop_list and len(prop_list) > 0 else "Información no disponible"

        api_external_APIkey_data = APIExternalData(
            cas_number=cas_number,
            description="\n".join(set(specific_properties.get("Physical Description", []))),
            solubility="\n".join(set(specific_properties.get("Solubility", []))),
            melting_point=extract_temp(specific_properties.get("Melting Point", [])),
            chemical_names=extract_first(specific_properties.get("IUPAC Name", [])),
            molecular_formula=extract_first(specific_properties.get("Molecular Formula", [])),
            molecular_weight=molecular_weight,
            log_p=extract_first(specific_properties.get("LogP", [])),
            boiling_point=extract_temp(specific_properties.get("Boiling Point", [])),
        )
        return {"api_external_APIkey_data": api_external_APIkey_data}

    async def run(self, state: LiteratureResearchGraphState):
        result = await self.search_external_apis(state)
        await self.client.aclose()
        return result
