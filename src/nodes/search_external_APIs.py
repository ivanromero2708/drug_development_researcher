import pubchempy as pcp
import httpx, asyncio, requests
from typing import Optional, Dict, Tuple, Union, List


class ExternalApiFunctions:
    CHEMBL_API_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

    def __init__(self):
        self.configurable = None

    # -------------Funciones de pubchem--------------------#
    # Obtener el CID
    def get_cid(inchikey: str) -> Optional[str]:
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
                print("No se encontró el compuesto con el InChIKey proporcionado")
                return None
        except pcp.PubChemHTTPError as e:
            print(f"Error de conexión con PubChem: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None

        # Obtener número CAS

    # Obtener número CAS
    def get_cas(smiles: str) -> str:
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
    async def get_specific_properties(cid: str) -> Optional[Dict]:
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
                ExternalApiFunctions.fetch_data_from_api(client, url, semaphore)
                for url in urls.values()
            ]
            responses = await asyncio.gather(*tasks)
            # Asignar los resultados a las propiedades correspondientes
            for property_name, response in zip(urls.keys(), responses):
                results[property_name] = response

        result = ExternalApiFunctions.extract_properties(results)

        return result

    # Extraer propiedades del API
    def extract_properties(data: dict) -> Dict[str, List[str]]:
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

    # -------------Funciones de chembl---------------------#
    # Función para obtener información de la API de CHEMBL
    def get_chembl_data(query_type: str, query: str) -> Optional[Dict]:
        """
        Fetches data from ChEMBL API based on query type and value.

        Args:
            query_type (str): Type of query (name or smiles).
            query (str): Query value.

        Returns:
            Optional[Dict]: JSON response from the API.
        """

        if query_type == "name":
            url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/molecule/search?q={query}&format=json"
        elif query_type == "smiles":
            url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/substructure/{query}?format=json&limit=21"
        else:
            return None

        try:
            response = requests.get(url, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            return response.json() if response.text.strip() else None
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud al API: {e}")
            return None

    # Función para obtener datos del compuesto (químico, mecanismo, indicaciones y propiedades)
    async def get_drug_data(
        chembl_id: str,
    ) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]:
        """
        Fetches drug data (market status, mechanism of action, indications) from ChEMBL.

        Args:
            chembl_id (str): ChEMBL ID for the compound.

        Returns:
            Tuple[Optional[Dict], Optional[Dict], Optional[Dict], Optional[Dict]]: Tuple containing drug, mechanism, indication and molecular data.
        """
        try:
            # Fetch approved drugs information
            drug_url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/drug?molecule_chembl_id={chembl_id}&format=json"
            mechanism_url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/mechanism?molecule_chembl_id={chembl_id}&format=json"
            indication_url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/drug_indication?molecule_chembl_id={chembl_id}&format=json"
            molecular_url = f"{ExternalApiFunctions.CHEMBL_API_BASE_URL}/molecule/{chembl_id}?format=json"

            # Lista de URLs
            urls = [drug_url, mechanism_url, indication_url, molecular_url]

            semaphore = asyncio.Semaphore(2)

            # Ejecutar las llamadas en paralelo
            async with httpx.AsyncClient() as client:
                tasks = [
                    ExternalApiFunctions.fetch_data_from_api(client, url, semaphore)
                    for url in urls
                ]
                responses = await asyncio.gather(*tasks)

            # Asignar valores a las variables
            drug_data, mechanism_data, indication_data, molecular_data = responses
            return drug_data, mechanism_data, indication_data, molecular_data
        except requests.exceptions.RequestException as e:
            print(f"Error al realizar la solicitud al API para datos de drogas: {e}")
            return None, None, None

    # -------------Funciones de ayuda----------------------#
    async def fetch_data_from_api(
        client: httpx.AsyncClient, url: str, semaphore: asyncio.Semaphore
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
                    print(f"Recurso no encontrado: {url}")
                    return None
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                print(f"Error al realizar la solicitud al API {url}: {e}")
                return None
