import streamlit as st
import json
from bs4 import BeautifulSoup
import requests
import re


def generate_html_report(categorized_abilities, original_filename):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Warhammer 40k Ability Reference Extractor</title>
        <style>
            /* Base Styles */
            body {{
                font-family: Arial, sans-serif; 
                margin: 10px; 
                background-color: rgb(250, 250, 255);
                font-size: 16px;
                line-height: 1.4;
                word-wrap: break-word;
            }}
            
            /* Responsive Typography */
            h1 {{
                color: rgb(25, 25, 103);
                text-align: center;
                border-bottom: 2px solid rgb(41, 128, 185);
                padding-bottom: 8px;
                font-size: clamp(1.5rem, 5vw, 2rem);
                margin: 15px 0;
            }}
            
            h2 {{
                color: rgb(204, 0, 100);
                border-bottom: 2px solid rgb(41, 128, 185);
                padding-bottom: 5px; 
                font-size: clamp(1.2rem, 4vw, 1.5rem);
                user-select: none;
                pointer-events: none;
            }}
            
            /* Mobile-First Layout */
            .phase-section {{
                background-color: rgb(245, 245, 255);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 15px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                border-left: 4px solid rgb(52, 152, 219);
            }}
            
            .ability {{
                position: relative;
                margin-bottom: 12px;
                padding: 10px;
                border-left: 4px solid rgb(41, 128, 185);
                background-color: rgb(240, 240, 250);
                transition: all 0.2s ease;
                overflow-wrap: break-word;
            }}
            
            .unit-name {{
                font-weight: bold;
                color: rgb(25, 25, 103);
                font-size: clamp(1rem, 3.5vw, 1.1rem);
            }}
            
            .ability-name {{
                font-weight: normal;
                font-style: italic;
                color: rgb(30, 30, 205);
                margin: 5px 0;
                font-size: clamp(0.95rem, 3.5vw, 1.05rem);
            }}
            
            .ability-desc {{
                white-space: pre-line;
                color: rgb(25, 25, 125);
                font-size: clamp(0.9rem, 3.2vw, 1rem);
                line-height: 1.5;
            }}
            
            /* Mobile-Specific Adjustments */
            @media (max-width: 600px) {{
                body {{
                    margin: 8px;
                    font-size: 14px;
                }}
                
                .phase-section {{
                    padding: 10px;
                }}
                
                .ability {{
                    padding: 8px;
                    margin-bottom: 10px;
                }}
                
                #save-button {{
                    padding: 8px 16px;
                    font-size: 14px;
                }}
            }}
            
            /* Existing interactive styles */
            .ability:hover {{
                background-color: rgb(250, 250, 255);
            }}
            
            .ability.dragging {{
                opacity: 0.5;
                background-color: rgb(250, 250, 255);
            }}
            
            #save-button {{
                display: block;
                margin: 15px auto;
                padding: 10px 20px;
                background-color: rgb(240, 240, 255);
                color: rgb(50, 50, 25);
                border: 1px solid rgb(100, 100, 255);
                border-radius: 3px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.2s;
            }}
            
            #save-button:hover {{
                background-color: rgb(150, 200, 255);
            }}
            
            .delete-btn {{
                position: absolute;
                top: 5px;
                right: 5px;
                background: none;
                border: none;
                color: rgb(180, 180, 180);
                cursor: pointer;
                font-size: 18px;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                opacity: 0;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
            }}
            
            .delete-btn:hover {{
                color: rgb(255, 255, 255);
                background-color: rgb(200, 0, 0);
            }}
            
            .ability:hover .delete-btn {{
                opacity: 1;
            }}
            @media print {{
                body {{ 
                    background-color: rgb(255, 255, 255);
                    color: rgb(0, 0, 0);
                }}
                .phase-section {{ 
                    box-shadow: none; 
                    page-break-inside: avoid;
                    background-color: rgb(255, 255, 255);
                    border-left: 2px solid rgb(0, 0, 0);
                }}
                .ability {{
                    background-color: rgb(255, 255, 255);
                    border-left: 2px solid rgb(0, 0, 0);
                }}
                .ability-name, .unit-name {{
                    color: rgb(0, 0, 0);
                }}
                .ability-desc {{
                    color: rgb(0, 0, 0);
                }}
                #save-button, .delete-btn {{ 
                    display: none; 
                }}
            }}
        </style>
    </head>
    <body>
        <h1>Warhammer 40k Ability Reference</h1>
        <button id="save-button">Save Current Order</button>
        {content}
        <script>
            let dragged;

            // Delete functionality
            function setupDeleteButtons() {{
                document.querySelectorAll('.delete-btn').forEach(btn => {{
                    btn.addEventListener('click', (e) => {{
                        e.stopPropagation();
                        if (confirm('Remove this ability from your reference?')) {{
                            e.target.closest('.ability').remove();
                        }}
                    }});
                }});
            }}

            document.addEventListener("DOMContentLoaded", () => {{
                // Initialize delete buttons
                setupDeleteButtons();
                
                // Drag and drop functionality
                const allAbilities = document.querySelectorAll(".ability");
                allAbilities.forEach(el => {{
                    el.setAttribute("draggable", "true");
                    el.addEventListener("dragstart", (e) => {{
                        dragged = e.target;
                        e.target.classList.add("dragging");
                    }});
                    el.addEventListener("dragend", (e) => {{
                        e.target.classList.remove("dragging");
                    }});
                }});

                const allDropZones = document.querySelectorAll(".phase-section");
                allDropZones.forEach(section => {{
                    section.addEventListener("dragover", (e) => {{
                        e.preventDefault();
                        const afterElement = getDragAfterElement(section, e.clientY);
                        if (!afterElement) {{
                            section.appendChild(dragged);
                        }} else {{
                            section.insertBefore(dragged, afterElement);
                        }}
                    }});
                }});

                document.getElementById("save-button").addEventListener("click", () => {{
                    const htmlContent = document.documentElement.outerHTML;
                    const blob = new Blob([htmlContent], {{ type: "text/html" }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = "{filename}";
                    document.body.appendChild(a);
                    a.click();
                    setTimeout(() => {{
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }}, 100);
                }});
            }});

            function getDragAfterElement(container, y) {{
                const draggableElements = [...container.querySelectorAll(".ability:not(.dragging)")];
                return draggableElements.reduce((closest, child) => {{
                    const box = child.getBoundingClientRect();
                    const offset = y - box.top - box.height / 2;
                    if (offset < 0 && offset > closest.offset) {{
                        return {{ offset: offset, element: child }};
                    }} else {{
                        return closest;
                    }}
                }}, {{ offset: Number.NEGATIVE_INFINITY }}).element;
            }}
        </script>
    </body>
    </html>
    """

    abilities_valid = []

    def bold_flagged_text(text):
        pattern = r"\*\*\^\^(.*?)\^\^\*\*"
        return re.sub(pattern, r"<strong>\1</strong>", text)

    phase_html = ""
    for phase, abilities in categorized_abilities.items():
        phase_html += f'<div class="phase-section">\n'
        phase_html += f'<h2>{phase}</h2>\n'

        for ability, description in abilities:
            unit_name = ability.split(":")[0].strip()
            ability_name = ability.split(":")[1].strip()

            description_bolded = bold_flagged_text(description)

            phase_html += f'<div class="ability">\n'
            phase_html += f'<button class="delete-btn" title="Remove ability">&#10005;</button>\n'
            phase_html += f'<div class="unit-name">{unit_name}</div>\n'
            phase_html += f'<div class="ability-name">{ability_name}</div>\n'
            phase_html += f'<div class="ability-desc">{description_bolded}</div>\n'
            phase_html += '</div>\n'

            abilities_valid.append([ability, description])

        phase_html += '</div>\n'


    # Use the original filename for the download
    download_filename = f"{original_filename}_reordered.html"
    return html_template.format(content=phase_html, filename=download_filename), abilities_valid


def extract_abilities_from_json(json_data):
    abilities = []
    detachment_abilities = []
    detachment_name = []

    def walk_selections(selections, current_unit=""):
        for item in selections:
            name = item.get("name", "")
            entry_id = item.get("entryId", "")

            # Check for detachment abilities
            if current_unit.lower() == "detachment" or name.lower() == "detachment":
                for sub in item.get("selections", []):
                    detachment_name_instance = sub.get("name", "")
                    detachment_name.append(detachment_name_instance)
                    for profile in sub.get("profiles", []):
                        if profile.get("typeName") == "Abilities":
                            ability_name = profile.get("name", "").strip()
                            description = next(
                                (char.get("$text", "").strip()
                                 for char in profile.get("characteristics", [])
                                 if char.get("name") == "Description"),
                                ""
                            )
                            detachment_abilities.append(("DETACHMENT ABILITY: " + ability_name, description))
                continue  # Skip depth search

            # Normal unit abilities
            if "profiles" in item:
                for profile in item["profiles"]:
                    if profile.get("typeName") == "Abilities":
                        ability_name = profile.get("name", "").strip()
                        description = next(
                            (char.get("$text", "").strip()
                             for char in profile.get("characteristics", [])
                             if char.get("name") == "Description"),
                            ""
                        )
                        label = f"{current_unit or name}: {ability_name}"
                        abilities.append((label, description))

            # Depth search
            if "selections" in item:
                walk_selections(item["selections"], current_unit or name)

    for force in json_data["roster"]["forces"]:
        walk_selections(force["selections"])

    return abilities, detachment_abilities, detachment_name


def extract_stratagems_from_waha(stratagems, detachment_name, url):
    st.success(f"Reading data from: {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for headers
    header_tag = None
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        found = soup.find(tag, string=lambda t: t and detachment_name in t)
        if found:
            header_tag = found
            break

    # Get content until the next header of the same type
    search_CP = ["1CP","2CP","3CP"]
    ref = []
    temp = []
    skip = 0

    for sibling in header_tag.find_next_siblings():
        if sibling.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:  # Stop at next header
            break
        
        text = sibling.get_text(strip=False).replace("\n\n","\n")

        for n, section in enumerate(text.split("\n")):
            if n == 0 and section.lower().startswith("stratagems"): section = section[10:]

            if section.strip() in search_CP:
                skip = 2
                try: del stratagems[-1][-1]
                except: pass

                ref, nr = temp[-1], -1
                while ref.strip() == "":
                    nr -= 1
                    ref = temp[nr]
                
                ref = ["Stratagem: " + ref.strip() + " " + section.strip()]
                stratagems.append(ref)

            elif stratagems and not skip:
                stratagems[-1].append(section.replace(".",".\n"))
            else: skip -= 1

            if section.strip() != "": temp.append(section.replace(".",".\n"))

    stratagems = [[x[0],x[1]] for x in stratagems if x]



def categorize_abilities(detachment_abilities, stratagems, abilities):
    phases = {
        "ANY PHASE": [],
        "COMMAND PHASE": [],
        "MOVEMENT PHASE": [],
        "SHOOTING PHASE": [],
        "CHARGE PHASE": [],
        "FIGHT PHASE": [],
        "OTHER": []
    }

    phase_keywords = {
        "FIGHT PHASE": ["fights", "fight phase", "weapon skill", "melee attack", "melee weapon"],
        "CHARGE PHASE": ["charge phase", "charge roll", "charge move"],
        "SHOOTING PHASE": ["shoot", "shooting phase", "ranged attack", "ranged weapon"],
        "MOVEMENT PHASE": ["move", "fallback", "fall back", "advance", "move phase", "movement phase", "deepstrike", "deep strike"],
        "COMMAND PHASE": ["start of your turn", "start of any turn", "start of the battleround", "command phase", "order", "battle-shock step", "battleshock step"],
        "ANY PHASE": ["any phase", "battle-shock test", "battleshock test", "makes an attack"]
    }

    abilities = detachment_abilities + stratagems + abilities

    for ability, description in abilities:
        desc_lower = description.lower()
        found = False

        for phase, keywords in phase_keywords.items():
            if any( " " + keyword in desc_lower for keyword in keywords):
                phases[phase].append((ability, description))
                found = True
                break

        if not found: phases["OTHER"].append((ability, description))

    return phases


def main():
    st.title("Warhammer 40k Ability Reference")
    st.markdown("""
    This App creates an ability reference from a New Recruit roster that can be viewed and reordered via HTML in any browser on desktop or mobile.
    
    1. Export your roster in New Recruit with Export -> JSON
    2. Upload the resulting listname.json here
    2. The App will extract and order all unit-abilities (if applicable)
    3. Download the reorderable HTML file and open it in a browser
    4. Reorder by drag & drop and modify as you wish
    5. Redownload your modified HTML file
    """)

    stratagems, detachment_abilities, detachment_name = [], [], None

    uploaded_file = st.file_uploader("Upload New Recruit JSON File", type=['json'])

    if uploaded_file is not None:
        try:
            original_filename = uploaded_file.name.split('.')[0]
            data = json.load(uploaded_file)

            abilities, detachment_abilities, detachment_name = extract_abilities_from_json(data)
            for x in detachment_abilities: print(x)


            if detachment_name:
                detachment_name = detachment_name[0]
                st.subheader(f"Detachment: {detachment_name}")

                url = st.text_input(
                    label="Enter Wahapedia Main-Faction URL for Stratagem Support:",
                    placeholder="e.g., https://wahapedia.ru/wh40k10ed/factions/space-marines")

                if url:
                    try:
                        extract_stratagems_from_waha(stratagems, detachment_name, url)
                        stratagems = [[x[0],x[1]] for x in stratagems if x]
                    except: st.warning("Stratagems can´t be extracted from the provided URL.")

            else: st.warning("Can´t find name of detachment.")

            with st.spinner("Processing JSON file..."):

                categorized = categorize_abilities(detachment_abilities, stratagems, abilities)
                html_report, abilities_valid = generate_html_report(categorized, original_filename)

                st.success("Extraction from JSON file complete.")
                
                st.download_button(
                    label="Download Reorderable HTML",
                    data=html_report,
                    file_name=f"{original_filename}_reordered.html",
                    mime="text/html")
        except:
            st.error("Extraction unsuccessful or data format incompatible.")

if __name__ == "__main__":
    main()
