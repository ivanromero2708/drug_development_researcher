import asyncio
import logging
import pandas as pd
import zipfile
import csv
from typing import List

from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.state import DrugDevelopmentResearchGraphState, RLD

class SearchOrangeBookCombined:
    """
    Node: SearchOrangeBookCombined

    Purpose:
      - If the user’s product is an RLD combination, we confirm the 'Ingredient' column has semicolons,
        plus partial matches for each API.
      - We also partial match dosage form & route from 'DF;Route'.
      - Exclude rows with Type == 'DSCN'.
      - Return first row that has RLD == 'YES'; if none found, fallback to RS == 'YES'.
      - Store brand_name, manufacturer as a single RLD object in state["RLDs"].
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

    def filter_combined_ingredients(
        self,
        df: pd.DataFrame,
        api_names: List[str],
        dosage_form: str,
        route_of_admin: str
    ) -> pd.DataFrame:
        """
        Steps:
          1) Exclude rows with Type == 'DSCN'.
          2) Ensure row['Ingredient'] has a semicolon => indicates multi-ingredient.
          3) For each row, partial-match all user-specified APIs in row['Ingredient'].
          4) Partial-match dosage_form & route_of_admin from 'DF;Route'.
        """
        # 1) Exclude DSCN
        mask_not_dscn = df['Appl_Type'].str.strip().str.upper() != "DSCN"

        # 2) row['Ingredient'] must have a semicolon => combination product
        mask_semicolon = df['Ingredient'].str.contains(';', na=False)

        # 3) Multi-API partial match
        #    row['Ingredient'] must contain all API names (case-insensitive)
        ingr_lower = df['Ingredient'].str.lower().fillna("")
        mask_apis = pd.Series([True]*len(df), index=df.index)
        for name in api_names:
            name_lower = name.lower().strip()
            mask_apis &= ingr_lower.str.contains(name_lower, na=False)

        # 4) Parse out dosage form & route
        df[['DosageForm', 'Route']] = df['DF;Route'].str.split(';', expand=True, n=1)
        df['DosageForm'] = df['DosageForm'].str.lower().str.strip()
        df['Route'] = df['Route'].str.lower().str.strip()

        mask_dosage = df['DosageForm'].str.contains(dosage_form.lower(), na=False)
        mask_route = df['Route'].str.contains(route_of_admin.lower(), na=False)

        # Combine
        return df[mask_not_dscn & mask_semicolon & mask_apis & mask_dosage & mask_route]

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
            return row.get("Trade_Name", ""), row.get("Applicant_Full_Name", ""), row.get("DosageForm", "")

        # Fallback to RS
        df_rs = df[df['RS'].str.strip().str.upper() == "YES"]
        if not df_rs.empty:
            row = df_rs.iloc[0]
            return row.get("Trade_Name", ""), row.get("Applicant_Full_Name", ""), row.get("DosageForm", "")

        # If none found
        return "", "", ""

    async def run(self, state: DrugDevelopmentResearchGraphState, config: RunnableConfig):
        """
        Single search for a combined-ingredient RLD:
         - Takes the entire list of APIs from state["apis"].
         - Expects 'Ingredient' to have a semicolon + partial matches for each API.
         - Also partial match dosage_form, route_of_admin from product_information.
         - Return the first row with RLD or RS == 'Yes'.
         - Store as a single RLD object in state["RLDs"] with brand_name, manufacturer.
        """
        try:
            # Load config
            configurable = Configuration.from_runnable_config(config)
            local_path = configurable.local_orange_book_zip_path

            # Load DataFrame
            products_text = self.load_and_extract_products(local_path)
            df_products = self.parse_products_file(products_text)

            # Build the list of API names
            apis = state["apis"]  # e.g. [ {API_name="Dronabinol"}, {API_name="Acetazolamide"} ]
            api_names = [api.API_name for api in apis]

            # Retrieve dosage_form, route_of_admin from product_information
            dosage_form = state["product_information"].product_dosage_form
            route_of_admin = state["product_information"].route_of_administration

            # Filter
            df_filtered = self.filter_combined_ingredients(
                df_products,
                api_names,
                dosage_form,
                route_of_admin
            )

            # RLD or RS
            brand, manufacturer, rld_dosage_form = self.find_first_rld_or_rs(df_filtered)

            # Build a single RLD object
            # For the 'api_name', we can join them with " + " for clarity
            combined_name = " + ".join(api_names)

            rld_item = RLD(
                api_name=combined_name,
                brand_name=brand.strip(),
                manufacturer=manufacturer.strip(),
                rld_dosage_form=rld_dosage_form.strip(),
            )

            # Store as a single-element list
            return {"RLDs": [rld_item]}

        except Exception as e:
            logging.error(f"Error in SearchOrangeBookCombined: {str(e)}")
            # If error, store empty list
            return {"RLDs": []}
