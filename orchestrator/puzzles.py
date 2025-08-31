from pydantic import BaseModel
from typing import List, Any, Dict

class Puzzle(BaseModel):
    id: str
    type: str
    description: str
    components: Dict[str, Any]
    solution: Any
    difficulty: str
