import asyncio
import logging
import pandas as pd
import zipfile
import io
import csv
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.rld_research_graph.state import RLDResearchGraphState

class SearchOrangeBook:
    def __init__(self, config: RunnableConfig):
        """
        Instead of downloading from the FDA site, we load the ZIP file from a local path.
        """
        configurable = Configuration.from_runnable_config(config)
        self.configurable = None
        # Path to the local Orange Book ZIP file (adjust as needed).
        self.local_orange_book_zip_path = configurable.local_orange_book_zip_path
    
    def load_and_extract_products(self):
        """
        Reads the OrangeBook zip file from a local path and extracts the products.txt file.
        """
        with zipfile.ZipFile(self.local_orange_book_zip_path, 'r') as zip_ref:
            # Look for the products.txt file (case-insensitive search)
            products_file_name = None
            for file_name in zip_ref.namelist():
                if "products.txt" in file_name.lower():
                    products_file_name = file_name
                    break
            if not products_file_name:
                raise Exception("products.txt not found in the local zip file.")
            
            # Read the file (ASCII text)
            with zip_ref.open(products_file_name) as f:
                products_text = f.read().decode('ascii', errors="replace")
        return products_text

    def parse_products_file(self, products_text):
        """
        Parses the tilde (~) delimited products.txt file into a list of dictionaries.
        Assumes the first line is a header.
        """
        reader = csv.DictReader(products_text.splitlines(), delimiter='~')
        products = list(reader)
        return products

    def filter_products(self, products, active_ingredient, desired_route, desired_dosage_form):
        """
        Filters products using pandas for efficient vectorized operations.
        
        Filtering criteria:
          1. 'Ingredient' must NOT contain ';' => ensures no combination products.
          2. 'Ingredient' must contain (case-insensitive partial match) the user-specified active_ingredient.
          3. 'RLD' must be "Yes" (case-insensitive).
          4. 'DF;Route' is split by ';' into DosageForm (first part) and Route (second part).
             Both must contain (case-insensitive partial match) the desired_dosage_form and desired_route.
        """
        df = pd.DataFrame(products)

        # 1. Exclude combination products: no semicolon in 'Ingredient'
        mask_no_semicolon = ~df['Ingredient'].str.contains(';', na=False)

        # 2. Partial match of the active_ingredient (case-insensitive)
        mask_active = df['Ingredient'].str.lower().str.contains(active_ingredient.lower().strip(), na=False)

        # 3. Filter by RLD == "Yes" (ignoring case)
        mask_rld = df['RS'].str.strip().str.upper() == "YES"

        # 4. Split "DF;Route" into DosageForm and Route, then partial-match both ignoring case
        dosage_route = df['DF;Route'].str.split(";", expand=True)
        if dosage_route.shape[1] >= 2:
            df['DosageForm'] = dosage_route[0].str.lower().str.strip()
            df['Route'] = dosage_route[1].str.lower().str.strip()
        else:
            df['DosageForm'] = ""
            df['Route'] = ""

        mask_dosage = df['DosageForm'].str.contains(desired_dosage_form.lower().strip(), na=False)
        mask_route = df['Route'].str.contains(desired_route.lower().strip(), na=False)

        # Combine all masks
        filtered_df = df[mask_no_semicolon & mask_active & mask_rld & mask_dosage & mask_route]
        return filtered_df.to_dict(orient='records')

    async def run(self, state: RLDResearchGraphState):
        """
        Expects state to contain:
            - "API_name": str (e.g., "Vonoprazan")
            - "route_of_administration": str (e.g., "oral")
            - "dosage_form": str (e.g., "tablet")
        
        Returns a dict with:
            - "brand_name": the Trade_Name
            - "manufacturer": the Applicant_Full_Name
        """
        try:
            active_ingredient = state.get("API").API_name
            desired_route = state.get("product_information_child").route_of_administration
            desired_dosage_form = state.get("API").desired_dosage_form
            
            if not active_ingredient or not desired_route or not desired_dosage_form:
                raise ValueError("Missing required parameters: API_name, route_of_administration, and dosage_form.")

            # Load the local products.txt data from the ZIP
            products_text = self.load_and_extract_products()
            products = self.parse_products_file(products_text)

            # Filter the data
            filtered_products = self.filter_products(products, active_ingredient, desired_route, desired_dosage_form)
            
            # Return the first filtered product, if any
            if filtered_products:
                prod = filtered_products[0]
                result = {
                    "brand_name": prod.get("Trade_Name", "").strip(),
                    "manufacturer": prod.get("Applicant_Full_Name", "").strip()
                }
            else:
                result = {"brand_name": "", "manufacturer": ""}
                
            return result
        except Exception as e:
            logging.error(f"Error in SearchOrangeBook: {str(e)}")
            return {"brand_name": "", "manufacturer": ""}

# Example usage for testing
if __name__ == "__main__":
    class DummyState(dict):
        def get(self, key, default=None):
            return super().get(key, default)

    dummy_state = DummyState({
        "API_name": "acetazolamide",
        "route_of_administration": "oral",
        "dosage_form": "tablet"
    })
    dummy_config = RunnableConfig()  # Adjust as needed

    search_node = SearchOrangeBook(dummy_config)

    async def test_run():
        result = await search_node.run(dummy_state, dummy_config)
        print(result)

    asyncio.run(test_run())
