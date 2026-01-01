"""
Clearbit API Client

Clearbit provides company and person enrichment data.
https://clearbit.com/docs

Features:
- Company enrichment (firmographics, tech stack, funding)
- Person enrichment
- Company name/domain resolution

Usage:
    from tools.clearbit import ClearbitClient
    
    client = ClearbitClient()
    
    # Enrich company
    company = client.enrich_company("example.com")
    
    # Enrich person
    person = client.enrich_person("john@example.com")
"""

from typing import Optional, Any
from tools.base import BaseAPIClient, get_credential, extract_domain


class ClearbitClient(BaseAPIClient):
    """Clearbit API client for enrichment data."""
    
    BASE_URL = "https://company.clearbit.com/v2"
    PERSON_URL = "https://person.clearbit.com/v2"
    
    def _get_headers(self) -> dict[str, str]:
        api_key = get_credential("clearbit", "api_key")
        return {
            "Authorization": f"Bearer {api_key}"
        }
    
    def enrich_company(self, domain: str) -> dict[str, Any]:
        """
        Enrich company data by domain.
        
        Args:
            domain: Company website domain
        
        Returns:
            {
                "id": "...",
                "name": "...",
                "legalName": "...",
                "domain": "...",
                "domainAliases": [...],
                "site": {...},
                "category": {...},
                "tags": [...],
                "description": "...",
                "foundedYear": int,
                "location": "...",
                "geo": {...},
                "logo": "...",
                "facebook": {...},
                "linkedin": {...},
                "twitter": {...},
                "crunchbase": {...},
                "emailProvider": bool,
                "type": "...",
                "ticker": "...",
                "identifiers": {...},
                "phone": "...",
                "metrics": {
                    "employees": int,
                    "employeesRange": "...",
                    "raised": int,
                    "annualRevenue": int,
                    "estimatedAnnualRevenue": "...",
                    ...
                },
                "tech": [...],
                "techCategories": [...],
                "parent": {...},
                "ultimateParent": {...}
            }
        """
        domain = extract_domain(domain)
        return self.get(f"/companies/find?domain={domain}")
    
    def enrich_person(
        self,
        email: str,
        include_company: bool = True
    ) -> dict[str, Any]:
        """
        Enrich person data by email.
        
        Args:
            email: Person's email address
            include_company: Include company data in response
        
        Returns:
            {
                "id": "...",
                "name": {...},
                "email": "...",
                "location": "...",
                "geo": {...},
                "bio": "...",
                "site": "...",
                "avatar": "...",
                "employment": {...},
                "facebook": {...},
                "github": {...},
                "twitter": {...},
                "linkedin": {...},
                "company": {...} (if include_company)
            }
        """
        # Use combined endpoint for person + company
        if include_company:
            url = f"https://person-stream.clearbit.com/v2/combined/find?email={email}"
        else:
            url = f"{self.PERSON_URL}/people/find?email={email}"
        
        return self.get(url.replace(self.BASE_URL, ""))
    
    def find_company(
        self,
        name: Optional[str] = None,
        domain: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Find company by name or domain.
        
        Args:
            name: Company name
            domain: Company domain
        
        Returns:
            Company data if found
        """
        if domain:
            return self.enrich_company(domain)
        elif name:
            # Use name-to-domain lookup
            return self.get(f"/companies/find?name={name}")
        else:
            raise ValueError("Provide either name or domain")
    
    def get_company_tech_stack(self, domain: str) -> list[str]:
        """
        Get technologies used by a company.
        
        Args:
            domain: Company domain
        
        Returns:
            List of technology names
        """
        company = self.enrich_company(domain)
        return company.get("tech", [])
    
    def get_company_metrics(self, domain: str) -> dict[str, Any]:
        """
        Get company metrics (employees, revenue, funding).
        
        Args:
            domain: Company domain
        
        Returns:
            Metrics dictionary
        """
        company = self.enrich_company(domain)
        return company.get("metrics", {})


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI entry point for Clearbit tools."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Clearbit enrichment data")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Company command
    company_parser = subparsers.add_parser("company", help="Enrich company")
    company_parser.add_argument("domain", help="Company domain")
    company_parser.add_argument("--tech", action="store_true", help="Show tech stack only")
    company_parser.add_argument("--metrics", action="store_true", help="Show metrics only")
    
    # Person command
    person_parser = subparsers.add_parser("person", help="Enrich person")
    person_parser.add_argument("email", help="Email address")
    person_parser.add_argument("--no-company", action="store_true", help="Exclude company data")
    
    args = parser.parse_args()
    client = ClearbitClient()
    
    try:
        if args.command == "company":
            if args.tech:
                result = client.get_company_tech_stack(args.domain)
                print("\nTech Stack:")
                for tech in result:
                    print(f"  • {tech}")
            elif args.metrics:
                result = client.get_company_metrics(args.domain)
                print("\nCompany Metrics:")
                print(json.dumps(result, indent=2))
            else:
                result = client.enrich_company(args.domain)
                print(json.dumps(result, indent=2))
        
        elif args.command == "person":
            result = client.enrich_person(
                args.email,
                include_company=not args.no_company
            )
            print(json.dumps(result, indent=2))
    
    finally:
        client.close()


if __name__ == "__main__":
    main()
