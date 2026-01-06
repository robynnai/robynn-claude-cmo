import os
import json
import sys
import httpx
from typing import Optional, Dict, Any, Generator

# ============================================================================
# Configuration
# ============================================================================

ROBYNN_API_BASE_URL = os.environ.get("ROBYNN_API_BASE_URL", "https://app.robynn.ai")

# ============================================================================
# Remote CMO Execution
# ============================================================================

class RemoteCMO:
    """Handles remote execution of CMO agent tasks via Robynn API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ROBYNN_API_KEY")
        self.base_url = ROBYNN_API_BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def stream_query(self, message: str) -> Generator[Dict[str, Any], None, None]:
        """Execute a query and stream the results/progress."""
        url = f"{self.base_url}/api/agents/cmo/stream"
        payload = {"message": message}
        
        try:
            with httpx.stream(
                "POST", 
                url, 
                json=payload, 
                headers=self._get_headers(),
                timeout=600.0
            ) as response:
                if response.status_code == 401:
                    yield {"type": "error", "message": "Unauthorized: Please check your ROBYNN_API_KEY"}
                    return
                elif response.status_code != 200:
                    yield {"type": "error", "message": f"Server error: {response.status_code}"}
                    return

                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        event_block, buffer = buffer.split("\n\n", 1)
                        event_data = self._parse_event(event_block)
                        if event_data:
                            yield event_data
        except Exception as e:
            yield {"type": "error", "message": f"Connection error: {str(e)}"}

    def _parse_event(self, block: str) -> Optional[Dict[str, Any]]:
        """Parse an SSE event block."""
        lines = block.strip().split("\n")
        event_type = "message"
        data_str = ""
        
        for line in lines:
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_str += line[5:].strip()
        
        if not data_str:
            return None
            
        try:
            return json.loads(data_str)
        except json.JSONDecodeError:
            # Fallback for non-JSON data
            return {"type": event_type, "message": data_str}

def main():
    """CLI entry point for remote execution."""
    if len(sys.argv) < 2:
        print("Usage: python tools/remote_cmo.py \"your query\"")
        sys.exit(1)
        
    query = sys.argv[1]
    cmo = RemoteCMO()
    
    print(f"\n[Robynn] Thinking about: {query[:50]}...")
    
    for event in cmo.stream_query(query):
        etype = event.get("type")
        msg = event.get("message")
        
        if etype == "status":
            print(f"  → {msg}")
        elif etype == "progress":
            print(f"  ⚙️  {msg}")
        elif etype == "complete":
            print("\n" + "="*80)
            data = event.get("data", {})
            print(data.get("response", "Done."))
            print("="*80)
            
            # Display usage if available
            usage = data.get("usage")
            if usage:
                remaining = usage.get("remaining")
                total = usage.get("total")
                if remaining is not None and total is not None:
                    print(f"✓ {remaining} of {total} tasks remaining this month.")
            print()
        elif etype == "error":
            print(f"\n❌ Error: {msg}")

if __name__ == "__main__":
    main()
