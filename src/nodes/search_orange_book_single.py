import asyncio
import logging
import pandas as pd
import zipfile
import csv
from typing import List

from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState, RLD
from pydantic import BaseModel, Field

class SearchOrangeBookSingle:
    """
    Node: SearchOrangeBookSingle

    Purpose:
      - For each API in state["apis"], search for a single-ingredient RLD in the Orange Book,
        using partial matches on Ingredient, dosage form, and route_of_administration.
      - Exclude Type == 'DSCN' and any Ingredient containing ';' (to ignore combos).
      - Attempt RLD == "Yes" first, fallback to RS == "Yes".
      - Build a list of RLD objects (api_name, brand_name, manufacturer).
      - Store that list in state["RLDs"].

    Output:
      - "RLDs": a list of RLD objects (matching your Pydantic definition).
    """

    def __init__(self):
        self.configurable = None

    def load_and_extract_products(self, local_zip_path: str) -> str:
        """
        Reads the Orange Book ZIP from local path, extracting 'products.txt' as a string.
        """
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            products_file_name = None
            for file_name in zip_ref.namelist():
                if "products.txt" in file_name.lower():
                    products_file_name = file_name
                    break
            if not products_file_name:
                raise FileNotFoundError("products.txt not found in the local zip file.")

            with zip_ref.open(products_file_name) as f:
                products_text = f.read().decode('ascii', errors="replace")
        return products_text

    def parse_products_file(self, products_text: str) -> pd.DataFrame:
        """
        Parses 'products.txt' (tilde-delimited) into a pandas DataFrame.
        """
        reader = csv.DictReader(products_text.splitlines(), delimiter='~')
        return pd.DataFrame(list(reader))

    def filter_for_single_api(
        self,
        df: pd.DataFrame,
        api_name: str,
        dosage_form: str,
        route_of_admin: str
    ) -> pd.DataFrame:
        """
        Filter logic for a single API:
          1) Exclude Type == 'DSCN'
          2) Exclude combination products: no semicolon in 'Ingredient'
          3) Partial match on 'Ingredient' with `api_name`
          4) Partial match for dosage form & route in 'DF;Route'
        """

        # 1) Exclude Type == 'DSCN'
        mask_not_dscn = df['Appl_Type'].str.strip().str.upper() != "DSCN"

        # 2) Exclude combination: no semicolon in Ingredient
        mask_no_semicolon = ~df['Ingredient'].str.contains(';', na=False)

        # 3) Partial match on Ingredient
        mask_ingredient = df['Ingredient'].str.lower().str.contains(api_name.lower(), na=False)

        # 4) Split "DF;Route" => DosageForm + Route
        df[['DosageForm', 'Route']] = df['DF;Route'].str.split(';', expand=True, n=1)
        df['DosageForm'] = df['DosageForm'].str.lower().str.strip()
        df['Route'] = df['Route'].str.lower().str.strip()

        # Partial match for dosage_form & route
        mask_dosage = df['DosageForm'].str.contains(dosage_form.lower(), na=False)
        mask_route = df['Route'].str.contains(route_of_admin.lower(), na=False)

        return df[mask_not_dscn & mask_no_semicolon & mask_ingredient & mask_dosage & mask_route]

    def find_first_rld_or_rs(self, df: pd.DataFrame):
        """
        1) Attempt RLD == 'Yes'
        2) If none, fallback to RS == 'Yes'
        3) Return brand_name, manufacturer from first row or ("","") if not found
        """
        # Attempt RLD first
        df_rld = df[df['RLD'].str.strip().str.upper() == "YES"]
        if not df_rld.empty:
            row = df_rld.iloc[0]
            return row.get("Trade_Name", ""), row.get("Applicant_Full_Name", ""), row.get("DosageForm", ""), row.get("Route", "")

        # Fallback to RS
        df_rs = df[df['RS'].str.strip().str.upper() == "YES"]
        if not df_rs.empty:
            row = df_rs.iloc[0]
            return row.get("Trade_Name", ""), row.get("Applicant_Full_Name", ""), row.get("DosageForm", ""), row.get("Route", "")

        # If none found
        return "", "", "", ""

    async def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        """
        For each API in state["apis"], do a single-ingredient Orange Book search.
        Build a list of RLD objects, store in state["RLDs"].
        """

        try:
            # Load config
            configurable = Configuration.from_runnable_config(config)
            local_path = configurable.local_orange_book_zip_path

            # Load DataFrame
            products_text = self.load_and_extract_products(local_path)
            df_products = self.parse_products_file(products_text)

            # Prepare a list for final RLD objects
            rld_list: List[RLD] = []

            # For each API
            apis = state["apis"]  # list of API objects
            for api_obj in apis:
                api_name = api_obj.API_name
                dosage_form = api_obj.desired_dosage_form  # literal field
                route_of_admin = api_obj.route_of_administration
                
                # Filter
                df_filtered = self.filter_for_single_api(df_products, api_name, dosage_form, route_of_admin)

                # Grab brand/manufacturer
                brand, manufacturer, rld_dosage_form, route_of_administration = self.find_first_rld_or_rs(df_filtered)

                # Build an RLD object
                rld_item = RLD(
                    api_name=api_name,
                    brand_name=brand.strip(),
                    manufacturer=manufacturer.strip(),
                    rld_dosage_form=rld_dosage_form.strip(),
                    route_of_administration = route_of_administration.strip(),
                )
                rld_list.append(rld_item)

            # Return for convenience
            return {"RLDs": rld_list}

        except Exception as e:
            logging.error(f"Error in SearchOrangeBookSingle: {str(e)}")
            # If error, store empty list
            return {"RLDs": []}

