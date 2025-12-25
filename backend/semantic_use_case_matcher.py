"""
Semantic Use Case Matcher
Maps natural language use cases to procurement categories using semantic keywords
"""

class SemanticUseCaseMatcher:
    """
    Semantic matcher that understands use cases and maps them to procurement categories
    Uses keyword expansion and semantic relationships
    """
    
    def __init__(self):
        # Semantic mapping: Use Case → Procurement Categories with keywords
        self.use_case_mappings = {
            # AUTOMOTIVE & VEHICLES
            'automotive': {
                'keywords': ['car', 'automobile', 'vehicle', 'auto', 'automotive', 'truck', 'suv', 'sedan', 'hyundai', 'toyota', 'ford', 'gm'],
                'categories': {
                    'Aluminum': {'priority': 1, 'reason': 'Body panels, engine blocks, wheels'},
                    'Steel': {'priority': 1, 'reason': 'Chassis, frame, structural components'},
                    'Plastics': {'priority': 2, 'reason': 'Interior components, bumpers, trim'},
                    'Copper': {'priority': 3, 'reason': 'Wiring, electrical systems'},
                    'IT Hardware': {'priority': 3, 'reason': 'Infotainment systems, sensors'},
                    'Manufacturing Equipment': {'priority': 2, 'reason': 'Assembly line equipment'}
                }
            },
            
            # IT & DATA CENTER
            'data_center': {
                'keywords': ['data center', 'datacenter', 'server farm', 'cloud infrastructure', 'hosting facility'],
                'categories': {
                    'IT Hardware': {'priority': 1, 'reason': 'Servers, storage, networking'},
                    'Network Equipment': {'priority': 1, 'reason': 'Switches, routers, firewalls'},
                    'Cloud Services': {'priority': 2, 'reason': 'Cloud infrastructure, backup'},
                    'Electricity': {'priority': 1, 'reason': 'Power supply, UPS systems'},
                    'Building Equipment': {'priority': 3, 'reason': 'Cooling systems, racks'}
                }
            },
            
            # CONSTRUCTION & BUILDING
            'construction': {
                'keywords': ['building', 'construction', 'infrastructure', 'facility', 'structure', 'edifice'],
                'categories': {
                    'Construction Materials': {'priority': 1, 'reason': 'Concrete, cement, aggregates'},
                    'Steel': {'priority': 1, 'reason': 'Structural steel, rebar'},
                    'Lumber': {'priority': 2, 'reason': 'Framing, formwork'},
                    'Building Equipment': {'priority': 2, 'reason': 'Tools, machinery'},
                    'Concrete': {'priority': 1, 'reason': 'Foundation, structure'}
                }
            },
            
            # HEALTHCARE & MEDICAL
            'healthcare': {
                'keywords': ['hospital', 'clinic', 'medical', 'healthcare', 'health facility', 'medical center'],
                'categories': {
                    'Medical Devices': {'priority': 1, 'reason': 'Diagnostic equipment, monitors'},
                    'Pharmaceuticals': {'priority': 1, 'reason': 'Medications, drugs'},
                    'Medical Supplies': {'priority': 1, 'reason': 'Consumables, PPE, instruments'},
                    'IT Hardware': {'priority': 3, 'reason': 'EMR systems, workstations'}
                }
            },
            
            # SOFTWARE & IT SERVICES
            'software_development': {
                'keywords': ['software', 'app', 'application', 'website', 'web app', 'mobile app', 'saas', 'platform'],
                'categories': {
                    'Cloud Services': {'priority': 1, 'reason': 'AWS, Azure, GCP hosting'},
                    'SaaS': {'priority': 1, 'reason': 'Development tools, collaboration'},
                    'Software Licenses': {'priority': 2, 'reason': 'IDEs, databases, frameworks'},
                    'Cybersecurity': {'priority': 2, 'reason': 'Security tools, monitoring'}
                }
            },
            
            # MANUFACTURING & PRODUCTION
            'manufacturing': {
                'keywords': ['manufacturing', 'factory', 'production', 'plant', 'assembly', 'fabrication'],
                'categories': {
                    'Manufacturing Equipment': {'priority': 1, 'reason': 'CNC, robotics, assembly lines'},
                    'Raw Materials': {'priority': 1, 'reason': 'Steel, aluminum, plastics'},
                    'Industrial Machinery': {'priority': 1, 'reason': 'Presses, lathes, mills'},
                    'Steel': {'priority': 2, 'reason': 'Raw material input'},
                    'Aluminum': {'priority': 2, 'reason': 'Raw material input'},
                    'Plastics': {'priority': 2, 'reason': 'Raw material input'}
                }
            },
            
            # ENERGY & UTILITIES
            'energy': {
                'keywords': ['power plant', 'energy', 'electricity', 'solar', 'wind', 'renewable', 'utility'],
                'categories': {
                    'Renewable Energy': {'priority': 1, 'reason': 'Solar panels, wind turbines'},
                    'Electricity': {'priority': 1, 'reason': 'Power generation equipment'},
                    'Solar Panels': {'priority': 1, 'reason': 'Photovoltaic systems'},
                    'Manufacturing Equipment': {'priority': 3, 'reason': 'Power plant equipment'}
                }
            },
            
            # OFFICE & CORPORATE
            'office': {
                'keywords': ['office', 'corporate', 'workplace', 'headquarters', 'branch'],
                'categories': {
                    'Office Supplies': {'priority': 1, 'reason': 'Stationery, consumables'},
                    'Office Furniture': {'priority': 1, 'reason': 'Desks, chairs, storage'},
                    'IT Hardware': {'priority': 2, 'reason': 'Laptops, printers, phones'},
                    'Telecommunications': {'priority': 2, 'reason': 'Phone systems, internet'}
                }
            },
            
            # LOGISTICS & WAREHOUSING
            'logistics': {
                'keywords': ['warehouse', 'distribution', 'logistics', 'supply chain', 'fulfillment'],
                'categories': {
                    'Warehousing': {'priority': 1, 'reason': 'Storage facilities, racking'},
                    'Logistics': {'priority': 1, 'reason': 'Transportation, freight'},
                    'Manufacturing Equipment': {'priority': 2, 'reason': 'Forklifts, conveyors'},
                    'IT Hardware': {'priority': 3, 'reason': 'WMS systems, scanners'}
                }
            }
        }
    
    def match_use_case(self, query: str) -> dict:
        """
        Match user query to procurement categories using semantic understanding
        
        Args:
            query: User's natural language query
            
        Returns:
            dict with matched categories, priorities, and reasons
        """
        query_lower = query.lower()
        matches = []
        
        # Check each use case for keyword matches
        for use_case, config in self.use_case_mappings.items():
            # Calculate match score based on keyword presence
            keyword_matches = sum(1 for keyword in config['keywords'] if keyword in query_lower)
            
            if keyword_matches > 0:
                match_score = keyword_matches / len(config['keywords'])
                matches.append({
                    'use_case': use_case,
                    'score': match_score,
                    'categories': config['categories'],
                    'matched_keywords': [kw for kw in config['keywords'] if kw in query_lower]
                })
        
        # Sort by match score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        if matches:
            # Return best match
            best_match = matches[0]
            
            # Get categories sorted by priority
            categories = sorted(
                best_match['categories'].items(),
                key=lambda x: x[1]['priority']
            )
            
            return {
                'use_case': best_match['use_case'],
                'confidence': best_match['score'],
                'matched_keywords': best_match['matched_keywords'],
                'categories': [
                    {
                        'name': cat_name,
                        'priority': cat_info['priority'],
                        'reason': cat_info['reason']
                    }
                    for cat_name, cat_info in categories
                ]
            }
        
        return None
    
    def get_search_terms(self, query: str) -> list:
        """
        Extract search terms from query based on semantic matching
        
        Args:
            query: User's query
            
        Returns:
            list of search terms for supplier database
        """
        match = self.match_use_case(query)
        
        if match:
            # Return category names as search terms
            return [cat['name'] for cat in match['categories'][:5]]  # Top 5 categories
        
        # Fallback: extract potential category keywords from query
        category_keywords = [
            'aluminum', 'steel', 'copper', 'plastics', 'concrete', 'lumber',
            'server', 'laptop', 'network', 'cloud', 'software',
            'medical', 'pharmaceutical', 'device',
            'equipment', 'machinery', 'robot',
            'office', 'furniture', 'supplies'
        ]
        
        return [kw for kw in category_keywords if kw in query.lower()]


# Example usage
if __name__ == "__main__":
    matcher = SemanticUseCaseMatcher()
    
    # Test cases
    test_queries = [
        "I'm making a car for Hyundai, looking for aluminum suppliers",
        "Building a new data center, need servers",
        "Hospital project, need medical equipment",
        "Software development, need cloud services",
        "Manufacturing facility, need equipment"
    ]
    
    print("="*80)
    print("SEMANTIC USE CASE MATCHER - TEST")
    print("="*80 + "\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        match = matcher.match_use_case(query)
        
        if match:
            print(f"  Use Case: {match['use_case']}")
            print(f"  Confidence: {match['confidence']:.2%}")
            print(f"  Matched Keywords: {', '.join(match['matched_keywords'])}")
            print(f"  Top Categories:")
            for cat in match['categories'][:3]:
                print(f"    {cat['priority']}. {cat['name']} - {cat['reason']}")
        else:
            print("  No match found")
        
        print()
