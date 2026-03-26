"""
Entity linking and disambiguation service.
Resolves extracted entities to canonical identifiers (Wikidata, etc.).
"""
import logging
from typing import Dict, List, Optional, Tuple
import json
import requests
from functools import lru_cache

logger = logging.getLogger(__name__)


class WikidataEntityLinker:
    """Resolves entities to Wikidata identifiers and metadata."""
    
    WIKIDATA_API = "https://www.wikidata.org/w/api.php"
    WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
    
    # Cache for common entities
    _entity_cache = {}
    
    @staticmethod
    def search_wikidata(query: str, language: str = "en") -> List[Dict]:
        """
        Search Wikidata for entity.
        
        Args:
            query: Entity name or description
            language: Language code
            
        Returns:
            List of matching entities with ID, label, description
        """
        try:
            params = {
                "action": "wbsearchentities",
                "search": query,
                "language": language,
                "format": "json",
                "limit": 5
            }
            
            response = requests.get(
                WikidataEntityLinker.WIKIDATA_API,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            results = response.json().get("search", [])
            return [
                {
                    "id": r.get("id"),
                    "label": r.get("label"),
                    "description": r.get("description"),
                    "match": r.get("match", {}).get("type")
                }
                for r in results
            ]
        except Exception as e:
            logger.debug(f"Wikidata search failed for '{query}': {e}")
            return []
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def get_entity_info(wikidata_id: str) -> Optional[Dict]:
        """
        Fetch full entity data from Wikidata.
        
        Args:
            wikidata_id: Wikidata Q-identifier
            
        Returns:
            Entity metadata: label, type, country, coordinates, etc.
        """
        try:
            params = {
                "action": "wbgetentities",
                "ids": wikidata_id,
                "format": "json",
                "props": "labels|descriptions|claims"
            }
            
            response = requests.get(
                WikidataEntityLinker.WIKIDATA_API,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            entity_dict = response.json().get("entities", {}).get(wikidata_id, {})
            if not entity_dict:
                return None
            
            # Extract labels and description
            labels = entity_dict.get("labels", {})
            descriptions = entity_dict.get("descriptions", {})
            claims = entity_dict.get("claims", {})
            
            return {
                "id": wikidata_id,
                "label": labels.get("en", {}).get("value"),
                "description": descriptions.get("en", {}).get("value"),
                "instance_of": WikidataEntityLinker._extract_instance_of(claims),
                "country": WikidataEntityLinker._extract_country(claims),
                "coordinate": WikidataEntityLinker._extract_coordinates(claims),
                "population": WikidataEntityLinker._extract_population(claims),
            }
        except Exception as e:
            logger.debug(f"Failed to fetch Wikidata {wikidata_id}: {e}")
            return None
    
    @staticmethod
    def _extract_instance_of(claims: Dict) -> Optional[str]:
        """Extract entity type (instance of)."""
        try:
            instance_claims = claims.get("P31", [])
            if instance_claims:
                return instance_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        except:
            pass
        return None
    
    @staticmethod
    def _extract_country(claims: Dict) -> Optional[str]:
        """Extract country property."""
        try:
            country_claims = claims.get("P17", [])
            if country_claims:
                return country_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        except:
            pass
        return None
    
    @staticmethod
    def _extract_coordinates(claims: Dict) -> Optional[Tuple[float, float]]:
        """Extract latitude, longitude."""
        try:
            coord_claims = claims.get("P625", [])
            if coord_claims:
                coords = coord_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {})
                return (coords.get("latitude"), coords.get("longitude"))
        except:
            pass
        return None
    
    @staticmethod
    def _extract_population(claims: Dict) -> Optional[int]:
        """Extract population (for regions/countries)."""
        try:
            pop_claims = claims.get("P1082", [])
            if pop_claims:
                return int(pop_claims[0].get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("amount", 0))
        except:
            pass
        return None
    
    @classmethod
    def link_entity(
        cls,
        entity_name: str,
        entity_type: str = None
    ) -> Optional[Dict]:
        """
        Link entity name to canonical Wikidata ID.
        
        Args:
            entity_name: Entity name (e.g., "India", "TSMC")
            entity_type: Optional entity type for disambiguation
            
        Returns:
            Wikidata entity info or None
        """
        # Check cache first
        cache_key = f"{entity_name}_{entity_type}"
        if cache_key in cls._entity_cache:
            return cls._entity_cache[cache_key]
        
        # Search Wikidata
        results = cls.search_wikidata(entity_name)
        if not results:
            return None
        
        # Use first result (highest match)
        best_match = results[0]
        entity_info = cls.get_entity_info(best_match["id"])
        
        # Cache result
        cls._entity_cache[cache_key] = entity_info
        return entity_info


class EntityAliasRegistry:
    """Maintain canonical aliases for entities (entity coreference resolution)."""
    
    # Hardcoded aliases (can be expanded)
    ALIASES = {
        "USA": ["United States", "US", "America", "U.S.A"],
        "China": ["PRC", "Communist China", "mainland China"],
        "India": ["Bharat", "Republic of India"],
        "Taiwan": ["Chinese Taipei", "ROC", "Formosa"],
        "Pakistan": ["Islamic Republic of Pakistan"],
        "Russia": ["USSR", "Soviet Union", "Russian Federation"],
        "UK": ["United Kingdom", "Britain", "Great Britain"],
        "Iran": ["Islamic Republic of Iran", "Persia"],
        "Saudi Arabia": ["KSA", "Saudi"],
        "Japan": ["Land of Rising Sun"],
        "Germany": ["FRG", "GDR", "Deutsches Reich"],
        "France": ["French Republic"],
        "EU": ["European Union"],
        "NATO": [],
        "BRICS": [],
        "QUAD": ["Quadrilateral Security Dialogue"],
        "RBI": ["Reserve Bank of India"],
        "TSMC": ["Taiwan Semiconductor"],
        "Fed": ["Federal Reserve", "US Federal Reserve"],
        "IMF": ["International Monetary Fund"],
        "World Bank": ["IBRD"],
    }
    
    @classmethod
    def resolve_alias(cls, entity_name: str) -> str:
        """
        Resolve alias to canonical name.
        
        Args:
            entity_name: Entity name
            
        Returns:
            Canonical entity name
        """
        # Check if input is canonical
        if entity_name in cls.ALIASES:
            return entity_name
        
        # Check if input is an alias
        for canonical, aliases in cls.ALIASES.items():
            if entity_name in aliases:
                return canonical
        
        # Not found; return as-is
        return entity_name
    
    @classmethod
    def register_alias(cls, canonical: str, alias: str):
        """Register new alias."""
        if canonical not in cls.ALIASES:
            cls.ALIASES[canonical] = []
        if alias not in cls.ALIASES[canonical]:
            cls.ALIASES[canonical].append(alias)
    
    @classmethod
    def get_all_forms(cls, entity_name: str) -> List[str]:
        """Get canonical + all aliases."""
        canonical = cls.resolve_alias(entity_name)
        return [canonical] + (cls.ALIASES.get(canonical, []) or [])
