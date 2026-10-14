from pathlib import Path

BASE = Path("documents/tourism_knowledge")
BASE.mkdir(parents=True, exist_ok=True)

documents = {

"taj_mahal.txt": """
Destination: Taj Mahal
Location: Agra, Uttar Pradesh
Category: Historical Monument / Cultural Tourism

The Taj Mahal is a white marble mausoleum located in Agra, Uttar Pradesh.
It was commissioned by Mughal emperor Shah Jahan in memory of Mumtaz Mahal.
Construction began in the 17th century and the monument is recognized as a
UNESCO World Heritage property.

Tourism relevance:
- Major cultural and heritage attraction
- Suitable for history and architecture-oriented travellers
- Can be combined with other Agra heritage attractions

Sustainable tourism considerations:
- Respect monument conservation rules
- Avoid littering
- Prefer shared/public transportation where practical
- Support local businesses and guides
- Avoid damaging or touching protected structures

Source:
UNESCO World Heritage Centre - Taj Mahal
https://whc.unesco.org/en/list/252
""",

"red_fort.txt": """
Destination: Red Fort
Location: Delhi
Category: Historical Monument / Cultural Tourism

The Red Fort is a major historical monument in Delhi and an important
example of Mughal architecture. The Red Fort Complex is recognized as a
UNESCO World Heritage property.

Tourism relevance:
- Suitable for history and architecture tourism
- Important cultural attraction in Delhi
- Can be combined with other heritage attractions in Delhi

Sustainable tourism considerations:
- Follow heritage-site regulations
- Use public transportation when practical
- Avoid littering
- Respect protected structures
- Support local businesses

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/list/
""",

"qutub_minar.txt": """
Destination: Qutb Minar
Location: Delhi
Category: Historical Monument / Cultural Tourism

Qutb Minar and its Monuments form an important historical complex in Delhi.
The site represents significant medieval Indian architecture and is
recognized as a UNESCO World Heritage property.

Tourism relevance:
- Suitable for history and architecture interests
- Important heritage attraction in Delhi
- Can be included in a multi-day Delhi itinerary

Sustainable tourism considerations:
- Follow site conservation rules
- Avoid littering
- Prefer public transport where practical
- Respect restricted areas

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/list/
""",

"mamallapuram.txt": """
Destination: Group of Monuments at Mahabalipuram (Mamallapuram)
Location: Tamil Nadu
Category: Heritage / Cultural Tourism

Mahabalipuram, also known as Mamallapuram, is located on the Coromandel
Coast of southeastern India. Its monuments include rock-cut caves,
monolithic temples, bas-reliefs and structural temples associated with
the Pallava period.

The Group of Monuments at Mahabalipuram is recognized as a UNESCO World
Heritage property.

Tourism relevance:
- Heritage and architecture tourism
- Suitable for history and cultural interests
- Coastal destination that can be combined with nearby attractions

Sustainable tourism considerations:
- Protect stone monuments from damage
- Avoid littering
- Respect archaeological restrictions
- Prefer shared transportation where possible
- Support local communities and businesses

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/list/249/
""",

"agra_fort.txt": """
Destination: Agra Fort
Location: Agra, Uttar Pradesh
Category: Historical Monument / Cultural Tourism

Agra Fort is a major historical fort complex in Agra and an important
example of Mughal architecture. It is recognized as a UNESCO World
Heritage property.

Tourism relevance:
- Suitable for heritage and history tourism
- Can be visited together with the Taj Mahal
- Useful for multi-attraction Agra itineraries

Sustainable tourism considerations:
- Follow conservation rules
- Avoid littering and damage to heritage structures
- Prefer shared transportation
- Support local tourism businesses

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/list/
""",

"golkonda_fort.txt": """
Destination: Golkonda Fort
Location: Hyderabad, Telangana
Category: Historical Monument / Cultural Tourism

Golkonda Fort is a historic fort complex associated with the Deccan region
and is an important cultural attraction in Hyderabad.

Tourism relevance:
- Suitable for history and architecture tourism
- Can be combined with other Hyderabad attractions
- Suitable for cultural tourism itineraries

Sustainable tourism considerations:
- Follow heritage-site regulations
- Avoid littering
- Protect historical structures
- Prefer public transportation or shared mobility
- Support local businesses

Source:
Archaeological Survey of India / Government tourism resources
""",

"konark.txt": """
Destination: Sun Temple, Konark
Location: Konark, Odisha
Category: Heritage / Cultural Tourism

The Sun Temple at Konark is a major historic temple complex in Odisha.
It is recognized as a UNESCO World Heritage property and is an important
example of Indian temple architecture.

Tourism relevance:
- Suitable for heritage and architecture tourism
- Important cultural attraction in Odisha
- Suitable for history-focused itineraries

Sustainable tourism considerations:
- Respect archaeological conservation requirements
- Avoid littering
- Do not damage or touch protected structures
- Support local communities
- Prefer sustainable transportation where available

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/list/
""",

"aguada_fort.txt": """
Destination: Fort Aguada
Location: Goa
Category: Historical Monument / Cultural Tourism

Fort Aguada is a historic fortification in Goa and an important heritage
attraction associated with the region's coastal history.

Tourism relevance:
- Suitable for heritage tourism
- Can be combined with other Goa attractions
- Suitable for travellers interested in history and coastal heritage

Sustainable tourism considerations:
- Respect protected structures
- Avoid littering
- Reduce unnecessary vehicle use
- Support local tourism businesses
- Respect the surrounding environment

Source:
Government tourism and heritage resources
""",

"chittorgarh_fort.txt": """
Destination: Chittorgarh Fort
Location: Chittorgarh, Rajasthan
Category: Heritage / Cultural Tourism

Chittorgarh Fort is a major historic fort complex in Rajasthan and forms
part of the Hill Forts of Rajasthan UNESCO World Heritage property.

Tourism relevance:
- Suitable for history and heritage tourism
- Important destination for Rajasthan cultural itineraries
- Suitable for architecture and historical interests

Sustainable tourism considerations:
- Respect heritage structures
- Follow conservation regulations
- Avoid littering
- Prefer shared transportation
- Support local guides and businesses

Source:
UNESCO World Heritage Centre
https://whc.unesco.org/en/statesparties/in/
""",

"shaniwarwada.txt": """
Destination: Shaniwarwada
Location: Pune, Maharashtra
Category: Historical Monument / Cultural Tourism

Shaniwarwada is a historic fortification and important heritage attraction
in Pune. It is associated with the history of the Maratha period.

Tourism relevance:
- Suitable for history and cultural tourism
- Can be included in Pune heritage itineraries
- Suitable for architecture and historical interests

Sustainable tourism considerations:
- Respect protected heritage areas
- Avoid littering
- Prefer public or shared transportation
- Support local businesses and guides

Source:
Government heritage and tourism resources
""",

"sustainable_tourism.txt": """
Topic: Sustainable Tourism

Sustainable tourism aims to reduce negative environmental impacts while
supporting local communities, cultural heritage and long-term tourism
development.

The AI Sustainable Tourism Planner uses the following sustainability
principles:

1. Sustainable Transportation
- Prefer walking and cycling for short distances
- Prefer public transportation where practical
- Consider shared transportation
- Compare transportation carbon emissions

2. Sustainable Accommodation
- Prefer accommodations with environmental practices
- Consider energy and water conservation
- Consider waste-management practices
- Consider recognized sustainability certifications where available

3. Local Community Support
- Recommend local restaurants and businesses
- Support local guides and artisans
- Encourage locally owned tourism services

4. Heritage Conservation
- Respect historical monuments
- Follow visitor regulations
- Avoid littering and physical damage
- Avoid overcrowding sensitive locations when alternatives exist

5. Environmental Protection
- Reduce unnecessary travel
- Reduce single-use plastic
- Encourage responsible waste disposal
- Prefer low-impact activities

6. Sustainable Itinerary Planning
The planner should consider:
- User budget
- Available travel time
- User interests
- Transportation distance
- Environmental impact
- Local community benefits

The system calculates a sustainability score by considering factors such
as transportation mode, estimated carbon impact, local-support practices
and environmentally responsible choices.

Official reference:
Ministry of Tourism, Government of India
National Strategy for Sustainable Tourism 2022
https://tourism.gov.in/guidelines-of-department/6639

Additional reference:
Sustainable Tourism Criteria for India
Ministry of Tourism, Government of India
https://tourism.gov.in/sites/default/files/2020-01/Document.pdf
"""
}

for filename, content in documents.items():
    path = BASE / filename
    path.write_text(content.strip(), encoding="utf-8")
    print(f"Created: {path}")

print("\nKnowledge base created successfully!")