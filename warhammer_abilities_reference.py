import streamlit as st
from bs4 import BeautifulSoup
import requests
import json
import re
import time
from weasyprint import HTML
from PIL import Image
import io

def generate_html_report(categorized_abilities, original_filename, url_core, url):
    timestamp = str(int(time.time()))
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
            transition: background-color 0.3s, color 0.3s;
        }}
        
        /* Dark Mode Styles */
        body.dark-mode {{
            background-color: rgb(30, 30, 40);
            color: rgb(220, 220, 230);
        }}
        
        body.dark-mode .phase-section {{
            background-color: rgb(40, 40, 50);
            border-left: 4px solid rgb(70, 130, 180);
        }}
        
        body.dark-mode .ability {{
            background-color: rgb(50, 50, 60);
            border-left: 4px solid rgb(70, 130, 180);
        }}
        
        body.dark-mode .unit-name {{
            color: rgb(180, 180, 255);
        }}
        
        body.dark-mode .ability-name {{
            color: rgb(150, 200, 255);
        }}
        
        body.dark-mode .ability-desc {{
            color: rgb(200, 200, 230);
        }}
        
        body.dark-mode h1 {{
            color: rgb(180, 180, 255);
            border-bottom: 2px solid rgb(70, 130, 180);
        }}
        
        body.dark-mode h2 {{
            color: rgb(255, 100, 150);
            border-bottom: 2px solid rgb(70, 130, 180);
        }}
        
        /* Custom Entry Form Styles - Light Mode */
        #custom-entry-container {{
            display: none;
            margin-bottom: 20px;
            display: flex; /* Side-by-side layout */
            gap: 20px; /* Space between form and notes */
        }}
        
        #custom-entry {{
            margin-bottom: 20px; 
            padding: 15px; 
            background: rgb(245, 245, 255); 
            border: 1px solid rgb(180, 180, 255); 
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(41, 128, 185, 0.15);
            flex: 1; /* Take available space */
            max-width: 35%; /* Limit form width */
        }}
        
        #custom-entry h2 {{
            margin-top: 0; 
            color: rgb(204, 0, 100);
            font-size: clamp(1.2rem, 4vw, 1.5rem);
            user-select: none;
            pointer-events: none;
            border-bottom: 2px solid rgb(41, 128, 185);
            padding-bottom: 5px;
        }}
        
        #custom-entry label {{
            display: block; 
            margin-bottom: 12px; 
            font-weight: bold; 
            color: rgb(30,30,205);
        }}
        
        #custom-entry select,
        #custom-entry input,
        #custom-entry textarea {{
            margin-top: 4px;
            padding: 6px 8px;
            font-size: 1rem;
            border: 1px solid rgb(150, 150, 255);
            border-radius: 4px;
            color: rgb(25, 25, 103);
            background-color: white;
            width: 100%;
            box-sizing: border-box;
        }}
        
        #custom-entry textarea {{
            resize: vertical;
            font-family: Arial, sans-serif;
            min-height: 100px;
        }}
        
        #custom-entry button {{
            padding: 10px 20px;
            background-color: rgb(240, 240, 255);
            color: rgb(50, 50, 25);
            border: 1px solid rgb(100, 100, 255);
            border-radius: 3px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
            display: block;
            margin-top: 5px;
        }}
        
        #custom-entry button:hover {{
            background-color: rgb(150, 200, 255);
        }}
        
        /* Custom Entry Form Styles - Dark Mode */
        body.dark-mode #custom-entry {{
            background: rgb(40, 40, 50);
            border: 1px solid rgb(70, 70, 100);
        }}
        
        body.dark-mode #custom-entry h2 {{
            color: rgb(255, 100, 150);
            border-bottom: 2px solid rgb(70, 130, 180);
        }}
        
        body.dark-mode #custom-entry label {{
            color: rgb(150, 200, 255);
        }}
        
        body.dark-mode #custom-entry select,
        body.dark-mode #custom-entry input,
        body.dark-mode #custom-entry textarea {{
            background-color: rgb(60, 60, 70);
            color: rgb(220, 220, 230);
            border: 1px solid rgb(80, 80, 120);
        }}
        
        body.dark-mode #custom-entry button {{
            background-color: rgb(60, 60, 80);
            color: rgb(220, 220, 230);
            border: 1px solid rgb(100, 100, 150);
        }}
        
        body.dark-mode #custom-entry button:hover {{
            background-color: rgb(80, 110, 150);
        }}
        
        /* Notes Container Styles */
        #custom-notes-container {{
            flex: 1; /* Take available space */
            max-width: 65%; /* Limit notes width */
            margin-bottom: 20px;
            padding: 15px;
            background: rgb(245, 245, 255);
            border: 1px solid rgb(180, 180, 255);
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(41, 128, 185, 0.15);
        }}
        
        #custom-notes-container h2 {{
            margin-top: 0;
            color: rgb(204, 0, 100);
            font-size: clamp(1.2rem, 4vw, 1.5rem);
            user-select: none;
            pointer-events: none;
            border-bottom: 2px solid rgb(41, 128, 185);
            padding-bottom: 5px;
        }}
        
        #custom-notes {{
            width: 100%;
            margin-top: 4px;
            padding: 6px 8px;
            font-size: 1rem;
            border: 1px solid rgb(150, 150, 255);
            border-radius: 4px;
            color: rgb(25, 25, 103);
            background-color: white;
            box-sizing: border-box;
            resize: vertical;
            font-family: Arial, sans-serif;
            min-height: 100px;
            height: 150px;
        }}
        
        /* Notes Container Styles - Dark Mode */
        body.dark-mode #custom-notes-container {{
            background: rgb(40, 40, 50);
            border: 1px solid rgb(70, 70, 100);
        }}
        
        body.dark-mode #custom-notes-container h2 {{
            color: rgb(255, 100, 150);
            border-bottom: 2px solid rgb(70, 130, 180);
        }}
        
        body.dark-mode #custom-notes {{
            background-color: rgb(60, 60, 70);
            color: rgb(220, 220, 230);
            border: 1px solid rgb(80, 80, 120);
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
            
            #save-button,
            #toggle-entry-btn,
            #dark-mode-toggle {{
                padding: 8px 16px;
                font-size: 14px;
            }}
            
            #custom-entry-container {{
                flex-direction: column;
            }}
            
            #custom-entry, #custom-notes-container {{
                max-width: 100%;
            }}
        }}
        
        /* Interactive styles */
        .ability:hover {{
            background-color: rgb(250, 250, 255);
        }}
        
        body.dark-mode .ability:hover {{
            background-color: rgb(60, 60, 70);
        }}
        
        .ability.dragging {{
            opacity: 0.5;
            background-color: rgb(250, 250, 255);
        }}
        
        #save-button,
        #toggle-entry-btn,
        #dark-mode-toggle {{
            display: block;
            padding: 5px 10px;
            background-color: rgb(240, 240, 255);
            color: rgb(50, 50, 25);
            border: 1px solid rgb(100, 100, 255);
            border-radius: 3px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        #save-button:hover,
        #toggle-entry-btn:hover,
        #dark-mode-toggle:hover {{
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

        .duplicate-btn {{
            position: absolute;
            top: 5px;
            right: 35px;
            background: none;
            border: none;
            color: rgb(150, 150, 200);
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

        .duplicate-btn:hover {{
            color: white;
            background-color: rgb(0, 123, 255);
        }}

        .ability:hover .duplicate-btn {{
            opacity: 1;
        }}

        .button-container {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }}
        
        .button-container button {{
            padding: 8px 5px;
            cursor: pointer;
        }}

        
        #aux-buttons {{
            display: inline-flex;
            gap: 20px;
            margin-left: 10px;
            vertical-align: middle;


        @media (max-width: 600px) {{
            #custom-entry-container {{
                flex-direction: column;
            }}
            #custom-entry, #custom-notes-container {{
                max-width: 100%;
            }}
        }}

        
        /* Common button styles */
        .button-global {{
            padding: 10px 20px;
            background-color: rgb(240, 240, 255);
            color: rgb(50, 50, 25);
            border: 1px solid rgb(100, 100, 255);
            border-radius: 3px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.2s;
            display: block;
            margin-top: 5px;
        }}

        .button-global:hover {{
            background-color: rgb(150, 200, 255);
        }}

        
        .button-global.link-button {{
            background-color: rgb(197, 213, 240);
            color: rgb(30, 30, 50);
            border: 1px solid rgb(29, 54, 94);
        }}

        .button-global.link-button:hover {{
            background-color: rgb(216, 224, 237);
        }}


        /* Dark mode button styles */
        body.dark-mode .button-global {{
            background-color: rgb(60, 60, 80);
            color: rgb(220, 220, 230);
            border: 1px solid rgb(100, 100, 150);
        }}

        body.dark-mode .button-global:hover {{
            background-color: rgb(80, 110, 150);
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
            #save-button, #toggle-entry-btn, #dark-mode-toggle, .delete-btn, .duplicate-btn {{ 
                display: none; 
            }}
        }}
    </style>

</head>
    <body>
        <h1>Warhammer 40k Ability Reference</h1>
        <div class="button-container">
            <button id="save-button" class="button-global">Save Current Order</button>
            <button id="toggle-entry-btn" class="button-global">Show Options</button>
            <button id="dark-mode-toggle" class="button-global">Toggle Dark Mode</button>
        </div>
        <div id="custom-entry-container" style="display: none;">
            <div id="custom-entry">
                <h2>Add Custom Entry</h2>
                <label>
                    Phase:
                    <select id="custom-phase">
                        <option value="DEPLOYMENT / RESERVES">Deployment / Reserves</option>          
                        <option value="ANY PHASE">Any Phase</option>
                        <option value="MOVEMENT PHASE">Movement Phase</option>
                        <option value="SHOOTING PHASE">Shooting Phase</option>
                        <option value="CHARGE PHASE">Charge Phase</option>
                        <option value="FIGHT PHASE">Fight Phase</option>
                        <option value="OTHER">Other</option>
                    </select>
                </label>
                <label>
                    Unit Name:
                    <input type="text" id="custom-unit"/>
                </label>
                <label>
                    Ability Name:
                    <input type="text" id="custom-name"/>
                </label>
                <label>
                    Ability Description:<br>
                    <textarea id="custom-desc" rows="4"></textarea>
                </label>
                <div id="aux-buttons">
                    <button onclick="addCustomAbility()" class="button-global">Add Entry</button>
                    <script>
                        const urlCore = "{url_core}";
                        if (urlCore && !document.querySelector('#aux-buttons a[href="' + urlCore + '"]')) {{
                            const coreLink = document.createElement('a');
                            coreLink.href = urlCore;
                            coreLink.target = '_blank';
                            coreLink.className = 'button-global link-button';
                            coreLink.textContent = 'Core Rules';
                            document.getElementById('aux-buttons').appendChild(coreLink);
                        }}
                        const urlFaction = "{url}";
                        if (urlFaction && !document.querySelector('#aux-buttons a[href="' + urlFaction + '"]')) {{
                            const factionLink = document.createElement('a');
                            factionLink.href = urlFaction;
                            factionLink.target = '_blank';
                            factionLink.className = 'button-global link-button';
                            factionLink.textContent = 'Faction Rules';
                            document.getElementById('aux-buttons').appendChild(factionLink);
                        }}
                    </script>
                </div>
            </div>
            <div id="custom-notes-container">
                <h2>Notes</h2>
                <textarea id="custom-notes" rows="4" placeholder="Enter notes here..."></textarea>
                <input type="hidden" id="saved-notes" value="">
            </div>
        </div>
        {content}
        <script>
            let dragged;

            // Dark mode toggle functionality
            document.getElementById("dark-mode-toggle").addEventListener("click", () => {{
                document.body.classList.toggle("dark-mode");
                const isDarkMode = document.body.classList.contains("dark-mode");
                localStorage.setItem("darkMode", isDarkMode);
            }});

            // Check for saved dark mode preference
            if (localStorage.getItem("darkMode") === "true") {{
                document.body.classList.add("dark-mode");
            }}

            // Save and load notes
            const notesTextarea = document.getElementById("custom-notes");
            const savedNotesInput = document.getElementById("saved-notes");
            notesTextarea.addEventListener("input", () => {{
                savedNotesInput.value = notesTextarea.value;
            }});
            if (savedNotesInput.value) {{
                notesTextarea.value = savedNotesInput.value;
            }}

            // Delete functionality
            function setupDeleteButtons() {{
                document.querySelectorAll('.delete-btn').forEach(btn => {{
                    btn.removeEventListener('click', handleDeleteClick);
                    btn.addEventListener('click', handleDeleteClick);
                }});
            }}

            function handleDeleteClick(e) {{
                e.stopPropagation();
                e.target.closest('.ability').remove();
            }}

            // Duplicate functionality
            function setupDuplicateButtons() {{
                document.querySelectorAll('.duplicate-btn').forEach(btn => {{
                    btn.removeEventListener('click', handleDuplicateClick);
                    btn.addEventListener('click', handleDuplicateClick);
                }});
            }}

            function handleDuplicateClick(e) {{
                e.stopPropagation();
                const ability = e.target.closest('.ability');
                const clone = ability.cloneNode(true);
                clone.id = 'ability-' + Math.random().toString(36).substr(2, 9);
                clone.setAttribute("draggable", "true");
                clone.addEventListener("dragstart", (e) => {{
                    dragged = e.target;
                    e.target.classList.add("dragging");
                }});
                clone.addEventListener("dragend", (e) => {{
                    e.target.classList.remove("dragging");
                }});
                clone.querySelector('.delete-btn').addEventListener('click', handleDeleteClick);
                clone.querySelector('.duplicate-btn').addEventListener('click', handleDuplicateClick);
                ability.after(clone);
            }}

            // Drag-and-drop setup
            function setupDragAndDrop() {{
                const allAbilities = document.querySelectorAll(".ability");
                allAbilities.forEach(el => {{
                    el.setAttribute("draggable", "true");
                    el.removeEventListener("dragstart", handleDragStart);
                    el.removeEventListener("dragend", handleDragEnd);
                    el.addEventListener("dragstart", handleDragStart);
                    el.addEventListener("dragend", handleDragEnd);
                }});

                const allDropZones = document.querySelectorAll(".phase-section");
                allDropZones.forEach(section => {{
                    section.removeEventListener("dragover", handleDragOver);
                    section.addEventListener("dragover", handleDragOver);
                }});
            }}

            function handleDragStart(e) {{
                dragged = e.target;
                e.target.classList.add("dragging");
                console.log('Dragging ability:', e.target.id); // Debug log
            }}

            function handleDragEnd(e) {{
                e.target.classList.remove("dragging");
                console.log('Dropped ability:', e.target.id); // Debug log
            }}

            function handleDragOver(e) {{
                e.preventDefault();
                const afterElement = getDragAfterElement(e.target.closest('.phase-section'), e.clientY);
                if (!afterElement) {{
                    e.target.closest('.phase-section').appendChild(dragged);
                }} else {{
                    e.target.closest('.phase-section').insertBefore(dragged, afterElement);
                }}
            }}

            document.addEventListener("DOMContentLoaded", () => {{
                setupDeleteButtons();
                setupDuplicateButtons();
                setupDragAndDrop();
                
                document.getElementById("save-button").addEventListener("click", () => {{
                    const clonedDoc = document.documentElement.cloneNode(true);
                    const auxButtons = clonedDoc.querySelector("#aux-buttons");
                    if (auxButtons) {{
                        const links = auxButtons.querySelectorAll("a");
                        links.forEach(link => link.remove());
                    }}
                    const htmlContent = clonedDoc.outerHTML;
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

            document.getElementById("toggle-entry-btn").addEventListener("click", () => {{
                const container = document.getElementById("custom-entry-container");
                if (container.style.display === "none" || container.style.display === "") {{
                    container.style.display = "flex";
                    document.getElementById("toggle-entry-btn").textContent = "Hide Options";
                }} else {{
                    container.style.display = "none";
                    document.getElementById("toggle-entry-btn").textContent = "Show Options";
                }}
            }});

            function addCustomAbility() {{
                const phase = document.getElementById("custom-phase").value;
                const unit = document.getElementById("custom-unit").value.trim();
                const name = document.getElementById("custom-name").value.trim();
                const desc = document.getElementById("custom-desc").value.trim();

                if (!unit || !name || !desc) {{
                    alert("Please fill in all fields.");
                    return;
                }}

                const abilityDiv = document.createElement("div");
                abilityDiv.className = "ability";
                abilityDiv.id = 'ability-' + Math.random().toString(36).substr(2, 9);
                abilityDiv.innerHTML = `
                    <button class="duplicate-btn" title="Duplicate ability">📑</button>
                    <button class="delete-btn" title="Remove ability">✕</button>
                    <div class="unit-name">${unit}</div>
                    <div class="ability-name">${name}</div>
                    <div class="ability-desc">${desc.replace(/\n/g, "<br>")}</div>
                `;

                abilityDiv.setAttribute("draggable", "true");
                abilityDiv.addEventListener("dragstart", handleDragStart);
                abilityDiv.addEventListener("dragend", handleDragEnd);

                abilityDiv.querySelector('.delete-btn').addEventListener('click', handleDeleteClick);
                abilityDiv.querySelector('.duplicate-btn').addEventListener('click', handleDuplicateClick);

                const section = [...document.querySelectorAll(".phase-section")].find(s =>
                    s.querySelector("h2")?.innerText === phase
                );
                if (section) {{
                    section.appendChild(abilityDiv);
                }} else {{
                    alert("Phase section not found.");
                }}

                document.getElementById("custom-unit").value = "";
                document.getElementById("custom-name").value = "";
                document.getElementById("custom-desc").value = "";
            }}
        </script>
    </body>
    </html>
    """

    def bold_flagged_text(text):
        pattern = r"\*\*\^\^(.*?)\^\^\*\*|\*\*(.*?)\*\*"
        return re.sub(pattern, lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", text)

    phase_html = ""
    for phase, abilities in categorized_abilities.items():
        phase_html += f'<div class="phase-section">\n'
        phase_html += f'<h2>{phase}</h2>\n'
        for idx, (ability, description) in enumerate(abilities):
            unit_name = ability.split(":")[0].strip()
            ability_name = ability.split(":")[1].strip()
            description_bolded = bold_flagged_text(description)
            phase_html += f'<div class="ability" id="ability-{phase.lower().replace(" / ","-").replace(" ","-")}-{idx}">\n'
            phase_html += f'<button class="duplicate-btn" title="Duplicate ability">📑</button>\n'
            phase_html += f'<button class="delete-btn" title="Remove ability">✕</button>\n'
            phase_html += f'<div class="unit-name">{unit_name}</div>\n'
            phase_html += f'<div class="ability-name">{ability_name}</div>\n'
            phase_html += f'<div class="ability-desc">{description_bolded}</div>\n'
            phase_html += f'</div>\n'
        phase_html += f'</div>\n'

    download_filename = f"{original_filename}_reordered.html"

    return html_template.format(
        css=html_template.split('<style>')[1].split('</style>')[0],
        content=phase_html,
        filename=download_filename,
        timestamp=timestamp,
        url_core=url_core or "",
        url=url or ""
    )

@st.cache_data
def extract_abilities_from_json(json_data):
    abilities = []
    detachment_abilities = []
    detachment_name = []

    def walk_selections(selections, current_unit=""):
        for item in selections:
            name = item.get("name", "")
            group = item.get("group", "")

            # Check for detachment abilities
            if (current_unit.lower() == "detachment" or 
                name.lower() == "detachment" or 
                group.lower() == "detachment"):
                
                # Get detachment name from this item or its selections
                if name and name.lower() != "detachment":
                    detachment_name_instance = name
                else:
                    for sub in item.get("selections", []):
                        detachment_name_instance = sub.get("name", "")
                        if detachment_name_instance:
                            break
                    else: detachment_name_instance = name
                
                if detachment_name_instance:
                    detachment_name.append(detachment_name_instance)

                # Check profiles for abilities
                for profile in item.get("profiles", []):
                    if profile.get("typeName") == "Abilities":
                        ability_name = profile.get("name", "").strip()
                        description = next(
                            (char.get("$text", "").strip()
                             for char in profile.get("characteristics", [])
                             if char.get("name") == "Description"),
                            ""
                        )
                        detachment_abilities.append(("DETACHMENT ABILITY: " + ability_name, description))
                
                # Check rules for abilities
                for rule in item.get("rules", []):
                    ability_name = rule.get("name", "").strip()
                    description = rule.get("description", "").strip()
                    if ability_name and description:
                        detachment_abilities.append(("DETACHMENT ABILITY: " + ability_name, description))

            # Normal unit abilities
            elif "profiles" in item:
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
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    def normalize(tt):
        return re.sub(r"[^a-zA-Z0-9]","", tt.lower()).replace(" ", "")

    # Look for headers
    search_name = normalize(detachment_name)
    header_tag = None
    for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        found = soup.find(tag, string=lambda t: t and search_name in normalize(t))
        if found:
            header_tag = found
            break

    if not header_tag:
        for tag in soup.find_all(['h2', 'h3', 'h4']):
            if search_name in normalize(tag.get_text(strip=True)):
                header_tag = tag
                break

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

def categorize_abilities(detachment_abilities, core_stratagems, stratagems, abilities, exclude_abilities):
    phases = {
        "DEPLOYMENT / RESERVES": [],
        "ANY PHASE": [],
        "COMMAND PHASE": [],
        "MOVEMENT PHASE": [],
        "SHOOTING PHASE": [],
        "CHARGE PHASE": [],
        "FIGHT PHASE": [],
        "OTHER": []
    }

    phase_keywords = {
        "FIGHT PHASE":    [" fight", " fights", " fight phase", " weapon skill", " melee attack", " melee attacks", " melee weapon", " melee weapons", " end of your opponents turn"],
        "CHARGE PHASE":   [" charge phase", " charge roll", " charge move"],
        "SHOOTING PHASE": [" shoot", " shooting phase", " ranged attack", " ranged attacks", " ranged weapon", " ranged weapons"],
        "MOVEMENT PHASE": [" moves", " a move", "normal move", " fallback", " fall back", " advance ", " move phase", " movement phase", " deepstrike", " deep strike"],
        "COMMAND PHASE":  [" start of your turn", " start of any turn", " start of the battleround", " start of your opponents turn", " command phase", " order", " battle-shock step", " battleshock step"],
        "ANY PHASE":      [" any phase", "each time", " each time", "battle shock", "battle-shock", " attack", " attacks", " weapon", " weapons", " stratagem"],
        "DEPLOYMENT / RESERVES": [" reserves", " declare battle formations", " scouts", " infiltrators"]
    }

    priority_order = ["start of", "declare battle formations", "infiltrators", "scouts", "after this", "until the end of", "until the start of", "end of"]
    priority_center = len(priority_order) // 2

    def priority_sort_key(s):
        s = s[1].lower()
        for i, p in enumerate(priority_order):
            if p in s: return i
        return priority_center

    abilities = detachment_abilities + core_stratagems + stratagems + abilities
    exclude_abilities = [x.lower() for x in exclude_abilities]

    for ability, description in abilities:
        parts = ability.split(":")
        if len(parts) < 2 or parts[1].lower().strip() in exclude_abilities:
            continue

        desc_lower = re.sub(r'\s+', ' ', description).strip().lower()
        description = description.replace("^^", "")
        description = re.sub(r"\b([A-Z]{2,})\b", r"**\1**", description)
        found = False

        for phase, keywords in phase_keywords.items():
            if found and phase == "ANY PHASE": break
            if any(keyword in desc_lower for keyword in keywords):
                phases[phase].append((ability, description))
                found = True

        if not found: phases["OTHER"].append((ability, description))

    for phase in phases:
        ability_count = {}
        renamed_abilities = {}
        
        for ability, description in phases[phase]:
            count = ability_count.get(ability, 0) + 1
            ability_count[ability] = count
            if count > 1: renamed_abilities[ability] = [str(count) + "x " + ability, description]
            else: renamed_abilities[ability] = [ability, description]

        renamed_abilities = list(renamed_abilities.values())
        renamed_abilities.sort(key=lambda x: x[0].split(":")[1].strip())
        renamed_abilities.sort(key=priority_sort_key)
        phases[phase] = renamed_abilities

    return phases

def convert_html_to_image(html_content, output_filename):
    try:
        html = HTML(string=html_content)
        img_data = html.write_png()
        img = Image.open(io.BytesIO(img_data))
        output_buffer = io.BytesIO()
        img.save(output_buffer, format="PNG")
        return output_buffer.getvalue(), f"{output_filename}.png"
    except Exception as e:
        st.error(f"Failed to convert HTML to image: {str(e)}")
        return None, None

def main():
    st.markdown("""
    <style>
    /* Title Style */
    h1 {
        text-align: center;
        color: #b0c4de;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
    }

    /* Form Style */
    .stForm {
        border: 1px solid #2a4b5b;
        border-radius: 5px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Warhammer 40k Ability Reference")
    st.markdown("""
    This App creates an ability reference from a New Recruit roster that can be viewed and reordered via HTML in any browser on desktop or mobile.
    
    1. Export your roster in New Recruit with Export -> JSON
    2. Upload the resulting listname.json here
    3. The App will extract and order all unit-abilities (if applicable)
    4. Download the reorderable HTML file and open it in a browser
    5. Reorder by drag & drop and modify as you wish
    6. Redownload your modified HTML file
    7. Optionally, upload the HTML file to convert it to an image
    """)

    # Session States
    if 'abilities' not in st.session_state:
        st.session_state.abilities = []
    if 'exclude_abilities' not in st.session_state:
        st.session_state.exclude_abilities = []
    if 'categorized' not in st.session_state:
        st.session_state.categorized = None
    if 'html_report' not in st.session_state:
        st.session_state.html_report = None
    if 'original_filename' not in st.session_state:
        st.session_state.original_filename = None
    if 'url' not in st.session_state:
        st.session_state.url = None
    if 'url_core' not in st.session_state:
        st.session_state.url_core = None
    if 'run_ok' not in st.session_state:
        st.session_state.run_ok = True
    if 'image_data' not in st.session_state:
        st.session_state.image_data = None
    if 'image_filename' not in st.session_state:
        st.session_state.image_filename = None

    # Input Form
    with st.form(key="input_form"):
        col1, col2 = st.columns(2)
        with col1:
            uploaded_json = st.file_uploader("Upload New Recruit JSON File", type=['json'])
        with col2:
            uploaded_html = st.file_uploader("Upload HTML File for Image Conversion", type=['html'])

        abilities_input = st.text_area(
            "Enter abilities or stratagems to exclude (one per line, e.g. Invulnuverable Save)",
            height=75 )

        url = st.text_input(
            label="Enter Wahapedia Main-Faction URL for Stratagem Support:",
            placeholder="e.g., https://wahapedia.ru/wh40kXXed/factions/space-marines" )

        core_strategems_option = st.checkbox("Include Core Stratagems aswell?", value=False)
        submit_button = st.form_submit_button("Process File")

        if submit_button and (uploaded_json is not None or uploaded_html is not None):
            # Process JSON file
            if uploaded_json is not None:
                if abilities_input:
                    st.session_state.exclude_abilities = [x.strip() for x in abilities_input.split("\n") if x.strip() != ""]

                st.session_state.original_filename = uploaded_json.name.rsplit('.')[0]
                st.session_state.url = url

                try:
                    data = json.load(uploaded_json)
                    abilities, detachment_abilities, detachment_name = extract_abilities_from_json(data)

                    stratagems, core_stratagems = [], []
                    if detachment_name:
                        detachment_name = detachment_name[0]
                        st.subheader(f"Detachment: {detachment_name}")

                        if url:
                            try:
                                reading_status = st.empty()
                                st.session_state.url_core = "/".join(url.split("/")[:4]) + "/the-rules/core-rules/"
                                if not core_strategems_option:
                                    reading_status.warning(f"Reading data from: {url}")
                                else:
                                    reading_status.warning(f"Reading data from: {url} and {st.session_state.url_core}")

                                extract_stratagems_from_waha(stratagems, detachment_name, url)
                                stratagems = [[x[0], x[1]] for x in stratagems if x]

                                if stratagems:
                                    reading_status.success("Detachment Stratagems were found and will be included.")

                                    if core_strategems_option:
                                        core_strategems_status = st.empty()
                                        extract_stratagems_from_waha(core_stratagems, "Stratagem", st.session_state.url_core)
                                        core_stratagems = [[x[0], x[1]] for x in core_stratagems if x]
                                        if core_stratagems:
                                            core_strategems_status.success("Core Stratagems were found and will be included.")
                                        else:
                                            core_strategems_status.warning("Core Stratagems can’t be and will not be included.")
                                else:
                                    reading_status.warning("Stratagems can’t be extracted from the provided spicified URL.")
                            except:
                                reading_status.warning("Stratagems can’t be extracted from the provided URL.")

                    with st.spinner("Processing JSON file..."):
                        st.session_state.categorized = categorize_abilities(
                            detachment_abilities, core_stratagems, stratagems, abilities, st.session_state.exclude_abilities
                        )
                        st.session_state.html_report = generate_html_report(
                            st.session_state.categorized, st.session_state.original_filename, st.session_state.url_core, st.session_state.url
                        )
                        st.success("Extraction from JSON file complete.")
                except:
                    st.error("Extraction unsuccessful or data format incompatible.")
                    st.session_state.run_ok = False

            # Process HTML file for image conversion
            if uploaded_html is not None:
                try:
                    with st.spinner("Converting HTML to image..."):
                        html_content = uploaded_html.read().decode('utf-8')
                        output_filename = uploaded_html.name.rsplit('.')[0]
                        st.session_state.image_data, st.session_state.image_filename = convert_html_to_image(html_content, output_filename)
                        if st.session_state.image_data:
                            st.success("HTML to image conversion complete.")
                        else:
                            st.session_state.run_ok = False
                except:
                    st.error("Failed to process HTML file for image conversion.")
                    st.session_state.run_ok = False

    # Download Buttons
    if st.session_state.html_report and st.session_state.run_ok:
        st.download_button(
            label="Download Reorderable HTML",
            data=st.session_state.html_report,
            file_name=f"{st.session_state.original_filename}_reordered.html",
            mime="text/html",
            key="download_button"
        )

    if st.session_state.image_data and st.session_state.run_ok:
        st.download_button(
            label="Download Image",
            data=st.session_state.image_data,
            file_name=st.session_state.image_filename,
            mime="image/png",
            key="image_download_button"
        )

if __name__ == "__main__":
    main()
