import asyncio
from typing import Dict, Any
from langchain_core.messages import AIMessage  # Opcional, para mensajes de feedback
from langchain_core.runnables import RunnableConfig
from ...configuration import Configuration
from ..state import LiteratureResearchGraphState

class EnrichDocuments:
    """
    Construye un string de contexto a partir de los documentos pertenecientes a los clusters seleccionados.
    Para cada URL válida (presente en state["documents"]), se extrae:
      - La URL
      - El raw_content (contenido completo extraído en la búsqueda)
      - El content (contenido breve o indexado)
    El string resultante se almacena en state["context"].
    """
    def __init__(self):
        pass

    async def curate(self, state: LiteratureResearchGraphState, config: RunnableConfig) -> Dict[str, Any]:
        chosen_clusters = state.get('chosen_clusters', [])
        clusters = state.get('document_clusters', [])
        context_parts = ""  # Inicializamos un string vacío para acumular el contenido

        configurable = Configuration.from_runnable_config(config)
                
        # Char limit for future prompts
        char_limit = configurable.max_tokens_per_source * 4
        
        # Para cada cluster seleccionado, se agregan los detalles de cada URL
        for cluster_index in chosen_clusters:
            try:
                cluster = clusters[cluster_index]
            except IndexError:
                continue
            # Agregar un encabezado para el cluster (opcional)
            context_parts += f"=== Cluster para la propiedad: {cluster.property} ===\n"
            for url in cluster.cluster:
                if url in state.get("documents", {}):
                    doc = state["documents"][url]
                    # Forzamos que si raw_content o content son None se usen cadenas vacías
                    raw_content = doc.get("raw_content") or ""
                    content = doc.get("content") or ""
                    context_parts += f"URL: {url}\n"
                    context_parts += "---- Raw Content ----\n"
                    context_parts += raw_content[:char_limit] + "... [truncated]" + "\n"
                    context_parts += "---- Content ----\n"
                    context_parts += content + "\n\n"
        return {"context": context_parts}

    async def run(self, state: LiteratureResearchGraphState, config: RunnableConfig) -> Dict[str, Any]:
        result = await self.curate(state, config)
        return result

# ----------------------------------------------------------------
# Código de test para verificar el nodo EnrichDocuments

if __name__ == "__main__":
    import asyncio
    from pydantic import BaseModel
    from typing import List

    # Modelos dummy para simular el estado
    class DummyAPI(BaseModel):
        API_name: str

    class DummyProductInformation(BaseModel):
        product_dosage_form: str
        route_of_administration: str

    class DummyCluster(BaseModel):
        property: str
        cluster: List[str]

    # Simulación de documentos recuperados (cada uno ya cuenta con "raw_content" y "content")
    dummy_documents = {
        "https://example.com/doc1": {
            "content": "Contenido breve sobre polymorphs.",
            "raw_content": "Contenido completo extraído sobre polymorphs desde Tavily."
        },
        "https://example.com/doc2": {
            "content": "Contenido breve sobre impurities y stability indicators.",
            "raw_content": "Contenido completo extraído sobre impurities y stability indicators desde Tavily."
        },
        "https://example.com/doc3": {
            "content": "Contenido breve sobre biopharmaceutical classification.",
            "raw_content": None  # Simulamos que raw_content viene como None
        }
    }

    # Simulación de clusters (por ejemplo, uno para "polymorphs" y otro para "impurities")
    dummy_clusters = [
        DummyCluster(property="polymorphs", cluster=["https://example.com/doc1", "https://example.com/doc2"]),
        DummyCluster(property="impurities", cluster=["https://example.com/doc2", "https://example.com/doc3"])
    ]

    # Construir un estado dummy similar a LiteratureResearchGraphState
    dummy_state = {
        "API": DummyAPI(API_name="Aspirin"),
        "product_information": DummyProductInformation(product_dosage_form="tablet", route_of_administration="oral"),
        "documents": dummy_documents,
        "document_clusters": dummy_clusters,
        # Se seleccionan ambos clusters
        "chosen_clusters": [0, 1]
    }

    # Configuración dummy (ajusta según la configuración de tu proyecto)
    from ...configuration import Configuration  # Asegúrate de que la ruta sea la correcta
    from langchain_core.runnables import RunnableConfig
    dummy_config = RunnableConfig(configurable=Configuration(number_of_queries=2, gpt4omini="gpt-4"))

    # Instanciar y ejecutar el nodo EnrichDocuments
    node = EnrichDocuments()
    result = asyncio.run(node.run(dummy_state, dummy_config))

    # Imprimir el contexto generado para inspección
    print("Contexto generado:")
    print(dummy_state.get("context", ""))
