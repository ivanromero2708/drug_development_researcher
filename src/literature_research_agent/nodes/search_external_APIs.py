import asyncio
import httpx
import logging
import re
import requests
import pubchempy as pcp
from typing import Optional, Dict, List
from pydantic import BaseModel
from src.literature_research_agent.state import LiteratureResearchGraphState, APIExternalData

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

class SearchExternalAPIs:
    """
    Nodo que evita el uso de la base de datos ChEMBL, y en su lugar
    obtiene la información necesaria de PubChem, incluyendo CID, CAS
    e isomeric SMILES.
    """
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

    def get_general_information(self, name: str) -> Optional[Dict]:
        """
        Busca el compuesto por 'name' en PubChem y extrae:
          - CID
          - SMILES isomérico
          - Número CAS (si lo encuentra entre los sinónimos)
        """
        compounds = pcp.get_compounds(name, "name")
        if compounds:
            compound = compounds[0]
            cid = compound.cid
            smiles = compound.isomeric_smiles
            sinonimos = compound.synonyms

            # Patrón para un número CAS: dígitos - dígitos - dígito
            patron_cas = re.compile(r"\d{2,7}-\d{2}-\d")
            cas_numbers = [s for s in sinonimos if patron_cas.match(s)]

            if cid and smiles and cas_numbers:
                return {
                    "cid": cid,
                    "smiles": smiles,
                    "cas_number": cas_numbers[0]
                }
            else:
                logging.warning("Información no disponible en PubChem para el CAS, CID o SMILES.")
        else:
            logging.warning(f"No se encontró el compuesto: {name}")
        return None

    async def get_specific_properties(self, cid: str) -> Dict[str, List[str]]:
        """
        Obtiene propiedades específicas del compuesto en PubChem
        (description, solubility, etc.) a través de endpoints JSON.
        """
        endpoints = {
            "Physical Description": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=physical+description",
            "Dissociation Constants": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Dissociation+Constants",
            "Stability conditions": f"{self.PUBCHEM_BASE_URL}{cid}/JSON?heading=Stability+/+Shelf+Life",
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
        Extrae cadenas 'String' de la estructura JSON devuelta por PubChem.
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
        Obtiene la información del compuesto a partir de PubChem:
        - CID, SMILES y CAS (get_general_information)
        - Peso molecular y propiedades específicas (get_specific_properties)
        """
        api_name = state["API"].API_name
        general_info = self.get_general_information(api_name)
        if not general_info:
            logging.error(f"No se pudo obtener información general para '{api_name}'.")
            return {"api_external_APIkey_data": None}

        cid = general_info["cid"]
        smiles = general_info["smiles"]
        cas_number = general_info["cas_number"]

        # Obtener peso molecular desde PubChem, usando el CID
        try:
            compounds = pcp.get_compounds(cid, "cid")
            compound = compounds[0] if compounds else None
            molecular_weight = getattr(compound, "molecular_weight", None) if compound else None
        except Exception as e:
            logging.error(f"Error al obtener peso molecular: {e}")
            molecular_weight = None

        # Obtener propiedades adicionales de PubChem
        specific_properties = await self.get_specific_properties(str(cid))

        def extract_temp(prop_list: List[str]) -> str:
            """Extrae la primera cadena que contenga 'XX °C', si existe."""
            for point in prop_list:
                if re.search(r"\d+\s?°C", point):
                    return point
            return prop_list[0] if prop_list else "Información no disponible"

        def extract_first(prop_list: List[str]) -> str:
            """Toma el primer valor de la lista, si existe."""
            return prop_list[0] if prop_list else "Información no disponible"

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
            pka = extract_first(specific_properties.get("Dissociation Constants", [])),
            stability = "\n".join(set(specific_properties.get("Stability conditions", []))),
        )

        return {"api_external_APIkey_data": api_external_APIkey_data}

    async def run(self, state: LiteratureResearchGraphState):
        """
        Método principal que se invoca desde el flujo. 
        Retorna un diccionario con la información obtenida.
        """
        result = await self.search_external_apis(state)
        await self.client.aclose()
        return result
