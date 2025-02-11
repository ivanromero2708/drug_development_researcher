import asyncio
from typing import Dict, Any
from langchain_core.messages import AIMessage  # Opcional, para mensajes de feedback
from langchain_core.runnables import RunnableConfig
from src.configuration import Configuration
from src.literature_research_agent.state import LiteratureResearchGraphState

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

