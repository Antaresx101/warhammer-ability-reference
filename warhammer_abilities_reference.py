import subprocess
import sys
import streamlit as st

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
try: from bs4 import BeautifulSoup
except ImportError:
    install("beautifulsoup4")
    from bs4 import BeautifulSoup

from html.parser import HTMLParser
from bs4 import BeautifulSoup
import requests
import re
from io import StringIO

abilities_valid = []

class AbilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_ability = False
        self.current_ability = ""
        self.current_description = ""
        self.abilities = []
        self.in_name_cell = False
        self.in_description_cell = False
        self.current_unit = ""
        self.in_unit_header = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr" and ("class", "section card-header") in attrs:
            self.in_unit_header = True
        if tag == "span" and ("class", "name") in attrs and self.in_unit_header:
            self.capture_unit_name = True
        if tag == "td" and ("class", "name cell") in attrs:
            self.in_name_cell = True
        elif tag == "td" and ("class", "characteristic small cell data") in attrs:
            self.in_description_cell = True

    def handle_data(self, data):
        if hasattr(self, 'capture_unit_name') and self.capture_unit_name:
            self.current_unit = data.strip()
            self.capture_unit_name = False
            self.in_unit_header = False
        elif self.in_name_cell:
            self.current_ability = data.strip()
        elif self.in_description_cell and self.current_ability:
            clean_data = data.replace("\n", " ").replace("\r", " ")
            self.current_description += clean_data

    def handle_endtag(self, tag):
        if tag == "td" and self.in_name_cell:
            self.in_name_cell = False
        elif tag == "td" and self.in_description_cell:
            self.in_description_cell = False
            if self.current_ability and self.current_description:
                cleaned_desc = re.sub(r'\s+', ' ', self.current_description).strip()
                label = f"{self.current_unit}: {self.current_ability.strip()}"
                self.abilities.append((label, cleaned_desc))
                self.current_ability = ""
                self.current_description = ""

def categorize_abilities(abilities, stratagems):
    phases = {
        "ANY PHASE / OTHER": [],
        "COMMAND PHASE": [],
        "MOVEMENT PHASE": [],
        "SHOOTING PHASE": [],
        "CHARGE PHASE": [],
        "FIGHT PHASE": [],
    }

    phase_keywords = {
        "FIGHT PHASE": ["fights", "fight phase", "weapon skill"],
        "CHARGE PHASE": ["charge phase", "charge roll", "charge move"],
        "SHOOTING PHASE": ["shoot", "shooting phase"],
        "MOVEMENT PHASE": ["move", "fallback", "fall back", "advance", "move phase", "movement phase", "deepstrike", "deep strike"],
        "COMMAND PHASE": ["start of your turn", "start of any turn", "start of the battleround", "command phase", "order", "battle-shock step", "battleshock step"],
        "ANY PHASE / OTHER": ["any phase", "battle-shock test", "battleshock test", "reserves", "redeploy"]
    }

    if stratagems: abilities = stratagems + abilities

    for ability, description in abilities:
        desc_lower = description.lower()

        for phase, keywords in phase_keywords.items():
            if any( " " + keyword in desc_lower for keyword in keywords):
                phases[phase].append((ability, description))
                break

    return phases

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

    phase_html = ""
    for phase, abilities in categorized_abilities.items():
        phase_html += f'<div class="phase-section">\n'
        phase_html += f'<h2>{phase}</h2>\n'

        for ability, description in abilities:
            unit_name = ability.split(":")[0].strip()
            ability_name = ability.split(":")[1].strip()

            phase_html += f'<div class="ability">\n'
            phase_html += f'<button class="delete-btn" title="Remove ability">&#10005;</button>\n'
            phase_html += f'<div class="unit-name">{unit_name}</div>\n'
            phase_html += f'<div class="ability-name">{ability_name}</div>\n'
            phase_html += f'<div class="ability-desc">{description}</div>\n'
            phase_html += '</div>\n'

            abilities_valid.append([ability, description])

        phase_html += '</div>\n'

    # Use the original filename for the download
    download_filename = f"{original_filename}_reordered.html"
    return html_template.format(content=phase_html, filename=download_filename), abilities_valid


def get_detachment_name(html_content):
    """Extracts detachment name from New Recruit HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Method 1: Search for specific pattern
    for div in soup.find_all('div'):
        if div.text.strip().startswith('• Detachment:'):
            option_name = div.find('span', class_='option-name')
            if option_name:
                return option_name.get_text(strip=True)
    
    # Method 2: Alternative search pattern
    for span in soup.find_all('span'):
        if span.text.strip() == 'Detachment':
            next_span = span.find_next('span', class_='option-name')
            if next_span:
                return next_span.get_text(strip=True)
    
    # Method 3: Fallback to regex search
    import re
    match = re.search(r'Detachment.*?option-name">(.*?)<', html_content)
    if match:
        return match.group(1).strip()
    return None


def main():
    st.title("Warhammer 40k Ability Reference Generator")
    st.markdown("""
    This App creates an ability reference from a New Recruit roster that can be viewed and reordered via HTML.
    
    1. Export your roster in New Recruit with Export -> "Pretty" or Export -> Templates -> "Pretty Cards"
    2. Upload the resulting listname.html here
    2. The App will extract and order all unit-abilities (if applicable)
    3. Download the reorderable HTML file and open it in a browser
    """)

    url = st.text_input(
        label="Enter Wahapedia Sub-Faction URL for Stratagem Support:",
        placeholder="e.g., https://wahapedia.ru/wh40k10ed/factions/space-marines/salamanders"
    )

    stratagems = []


    """ Rules-Extraction """
    uploaded_file = st.file_uploader("Upload New Recruit HTML File", type=['html'])
    
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        html_content = stringio.read()


        detachment_name = get_detachment_name(html_content)
        if detachment_name:
            st.subheader(f"Detachment: {detachment_name}")
        else:
            st.warning("Can´t find name of detachment.")

        if detachment_name and not url: st.warning("You can add Stratagems by providing the wahapedia.ru page of your army.")

        elif detachment_name:
            try:
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
            except:
                if detachment_name and url: st.warning("Stratagems can´t be extracted from the provided URL.")


        # Abilities
        original_filename = uploaded_file.name.split('.')[0]

        with st.spinner("Processing HTML file..."):
            parser = AbilityParser()
            parser.feed(html_content)
            abilities = parser.abilities

            categorized = categorize_abilities(abilities, stratagems)
            html_report, abilities_valid = generate_html_report(categorized, original_filename)

            st.success(f"Extraction complete.")
            
            st.download_button(
                label="Download Reorderable HTML",
                data=html_report,
                file_name=f"{original_filename}_reordered.html",
                mime="text/html"
            )
            
            if abilities_valid:
                st.markdown("### Preview (first 5 abilities)")
                for i, (ability, desc) in enumerate(abilities_valid[:5]):
                    st.markdown(f"**{ability}**")
                    st.markdown(f"{desc}")
                    if i < 4:
                        st.divider()

if __name__ == "__main__":
    main()
