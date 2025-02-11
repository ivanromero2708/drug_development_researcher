import pubchempy as pcp
import httpx, asyncio, logging
from typing import Optional, Dict, Union, List
from src.literature_research_agent.state import LiteratureResearchGraphState, APIExternalData
from langchain_core.runnables import RunnableConfig
import re

class SearchExternalAPIs:
    CHEMBL_API_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

    def __init__(self):
        self.configurable = None

    # Funciones de pubchem
    # get_cid, get_cas, get_specific_properties, extract_properties
    # Funciones de chembl
    # get_chembl_data
    # Funciones auxiliares
    # fetch_data_from_api

    # Función para obtener información de la API de CHEMBL
    async def get_chembl_data(self, name: str) -> Optional[Dict]:
        """
        Fetches data from ChEMBL API based on Compound name.

        Args:
            name (str): Compound name.

        Returns:
            Optional[Dict]: JSON response from the API.
        """

        url = f"{self.CHEMBL_API_BASE_URL}/molecule/search?q={name}&format=json"
        semaphore = asyncio.Semaphore(1)

        async with httpx.AsyncClient(
            headers={"Content-Type": "application/json"}
        ) as client:
            return await self.fetch_data_from_api(client, url, semaphore)

    # Obtener el CID
    def get_cid(self, inchikey: str) -> Optional[str]:
        """
        Get the cid with the inchikey of a compound.

        Args:
            inchikey (str): Inchikey of a compound.

        Returns:
            compounds (str): Cid of a compound or None.
        """

        try:
            compounds = pcp.get_compounds(inchikey, namespace="inchikey")

            if compounds:
                return compounds[0].cid
            else:
                logging("No se encontró el compuesto con el InChIKey proporcionado")
                return None
        except pcp.PubChemHTTPError as e:
            logging(f"Error de conexión con PubChem: {e}")
            return None
        except Exception as e:
            logging(f"Error inesperado: {e}")
            return None

        # Obtener número CAS

    # Obtener número CAS
    def get_cas(self, smiles: str) -> str:
        """
        Obtain Cas Number with SMILES.

        Args:
            smiles (str): SMILES or Cannonical SMILES.
        Returns:
            syn (str): CAS Number or message error
        """
        try:
            # Buscar compuestos en PubChem usando SMILES
            compounds = pcp.get_compounds(smiles, "smiles")

            if compounds:
                # Obtener los sinónimos del primer compuesto encontrado
                synonyms = compounds[0].synonyms

                # Buscar el número CAS en los sinónimos
                for syn in synonyms:
                    # El número CAS sigue el formato XXXX-XX-X
                    if "-" in syn and syn.replace("-", "").isdigit():
                        return syn

            return "No disponible"
        except Exception as e:
            return f"Error: {e}"

    # Obtener JSON de la API de PubChem
    async def get_specific_properties(self, cid: str) -> Optional[Dict]:
        """
        Fetch the API endpoint to obtain melting point,boiling point,
        density, pKa, LogP, stability, solubility, description and
        storage conditions

        Args: cid (str): Compound id

        Returns:
            dict: A dictionary containing all fetched properties.
        """

        base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"

        # Url para cada propiedad
        urls = {
            "description_url": f"{base_url}{cid}/JSON?heading=physical+description",
            "pka_url": f"{base_url}{cid}/JSON?heading=Dissociation+Constants",
            "log_url": f"{base_url}{cid}/JSON?heading=LogP",
            "solubility_url": f"{base_url}{cid}/JSON?heading=solubility",
            "storage_url": f"{base_url}{cid}/JSON?heading=storage+conditions",
            "melting_url": f"{base_url}{cid}/JSON?heading=Melting+Point",
            "boiling_url": f"{base_url}{cid}/JSON?heading=Boiling+Point",
            "molecular_url": f"{base_url}{cid}/JSON?heading=Molecular+Formula",
            "iupac_url": f"{base_url}{cid}/JSON?heading=IUPAC+Name",
        }

        semaphore = asyncio.Semaphore(1)  # Número de solicitudes simultaneas
        results = {}
        async with httpx.AsyncClient() as client:
            tasks = [
                self.fetch_data_from_api(client, url, semaphore)
                for url in urls.values()
            ]
            responses = await asyncio.gather(*tasks)
            # Asignar los resultados a las propiedades correspondientes
            for property_name, response in zip(urls.keys(), responses):
                results[property_name] = response

        result = self.extract_properties(results)

        return result

    # Extraer propiedades del API
    def extract_properties(self, data: dict) -> Dict[str, List[str]]:
        """
        Extract specific information from the APIs.

        Args:
            data (Dict): Dictionary that represents a structure of JSON

        Returns:
            Dict[str, List[str]]: Dictionary with a list of values extracts from JSON.
        """
        # Diccionario donde se guardan las propiedades
        results = {
            "Physical Description": [],
            "Melting Point": [],
            "Boiling Point": [],
            "Density": [],
            "Dissociation Constants": [],
            "LogP": [],
            "Solubility": [],
            "Storage Conditions": [],
            "Molecular Formula": [],
            "IUPAC Name": [],
        }

        # Mapeo de TOCHeading
        toc_heading_map = {
            "Physical Description": "Physical Description",
            "Melting Point": "Melting Point",
            "Boiling Point": "Boiling Point",
            "Density": "Density",
            "Dissociation Constants": "Dissociation Constants",
            "LogP": "LogP",
            "Solubility": "Solubility",
            "Storage Conditions": "Storage Conditions",
            "Molecular Formula": "Molecular Formula",
            "IUPAC Name": "IUPAC Name",
        }

        # Función recursiva para buscar en la estructura del JSON
        def recursive_search(obj: Union[dict, list, any]):
            """
            Recursive search to extract specific information from JSON.

            Args:
            obj (Union[dict, list, Any]):
                -If dict, iterate on the keys and values to search for specific keys.
                -If list, iterate on elements and recursively calls this function.
                -If any (string, number, etc.), don't make any aditional action.

            Note:
                This function modify the dictionary of extract_properties.
            """
            if isinstance(
                obj, dict
            ):  # Si es un diccionario, busca dentro de sus valores
                for key, value in obj.items():
                    if key == "TOCHeading" and value in toc_heading_map:
                        property_name = toc_heading_map[value]
                        if "Information" in obj:
                            for info in obj["Information"]:
                                if (
                                    "Value" in info
                                    and "StringWithMarkup" in info["Value"]
                                ):
                                    for item in info["Value"]["StringWithMarkup"]:
                                        if "String" in item:
                                            results[property_name].append(
                                                item["String"]
                                            )
                    else:
                        recursive_search(value)
            elif isinstance(obj, list):  # Si es una lista, itera sobre sus elementos
                for item in obj:
                    recursive_search(item)

        # Iterar sobre todas las propiedades en los datos
        for property_data in data.values():
            if property_data is not None:  # Ignorar propiedades sin datos
                recursive_search(property_data)
        return results

    # Funcion para extraer información del api
    async def fetch_data_from_api(
        self, client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore
    ) -> Optional[Dict]:
        """
        Fetches data from an API endpoint using httpx.

        Args:
            client (httpx.AsyncClient): The HTTP client.
            url (str): URL to fetch data from.

        Returns:
            dict or None: JSON response if successful, otherwise None.
        """
        async with semaphore:  # Limitar el número de solicitudes al servidor
            try:
                response = await client.get(url)
                if response.status_code == 404:
                    logging(f"Recurso no encontrado: {url}")
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                logging(f"Error al realizar la solicitud al API {url}: {e}")
                return None

    async def search_external_apis(self, state: LiteratureResearchGraphState, config: RunnableConfig):
        api_name = state["API"].API_name
        
        chembl_json = self.get_chembl_data(name = api_name)
        molecule = chembl_json["molecules"][0]
        molecule_structures = molecule.get("molecule_structures", {})
        
        smiles = molecule_structures.get("canonical_smiles", "NA")
        InChI = molecule_structures.get("standard_inchi", "NA")
        InChiKey = molecule_structures.get("standard_inchi_key", "NA")
        
        cas_number = self.get_cas(smiles)
        
        cid = self.get_cid(InChiKey)
        compound = pcp.get_compounds(InChiKey, "inchi_key")
        
        # Molecular weight
        molecular_weight = compound.molecular_weight
        
        specific_properties = await self.get_specific_properties(cid)
        
        # API Physical description
        unique_physical = set(specific_properties["Physical Description"])
        physical_description = "\n" + "\n".join(
            f"- {point}" for point in unique_physical
        )
        
        # API solubility
        unique_solubility = set(specific_properties["Solubility"])
        solubility = "\n" + "\n".join(
            f"- {point}" for point in unique_solubility
        )
        
        # Melting point
        celsius_value = None
        for point in specific_properties["Melting Point"]:
            if re.search(r"\d+ °C", point):
                celsius_value = point
                break
 
        if celsius_value:
            melting_point = f"{celsius_value}"
        else:
            melting_point = (
                f"{specific_properties["Melting Point"][0]}"
                if specific_properties["Melting Point"]
                else "Información no disponible"
            )
        
        # Chemical names
        unique_iupac = set(specific_properties["IUPAC Name"])
        first_value = list(unique_iupac)[0]
        iupac_name = f"{first_value}"
        
        # Molecular Structure
        unique_molecular = set(specific_properties["Molecular Formula"])
        first_value = list(unique_molecular)[0]
        molecular_formula = f"{first_value}"
        
        # LogP
        unique_logp = set(specific_properties["LogP"])
        first_value = list(unique_logp)[0]
        logp = f"{first_value}"
        
        # pKa Dissociation Constant
        unique_pka = set(specific_properties["Dissociation Constants"])
        first_value = list(unique_pka)[0]
        pka = f"{first_value}"
        
        # Boiling Point
        celsius_value = None
 
        for point in specific_properties["Boiling Point"]:
            if re.search(r"\d+ °C", point):
                celsius_value = point
                break
 
        if celsius_value:
            boiling_point = f"{celsius_value}"
        else:
            boiling_point = (
                f"{specific_properties["Boiling Point"][0]}"
                    if specific_properties["Boiling Point"]
                else "Información no disponible"
            )
        
        api_external_APIkey_data = APIExternalData(
            cas_number = cas_number,
            description = physical_description,
            solubility = solubility,
            melting_point = melting_point,
            chemical_names = iupac_name,
            molecular_formula = molecular_formula,
            molecular_weight = molecular_weight,
            log_p = logp,
            boiling_point=boiling_point,
            )
        
        return {"api_external_APIkey_data": api_external_APIkey_data}
    
    def run(self, state, config):
        return self.run(state,config)