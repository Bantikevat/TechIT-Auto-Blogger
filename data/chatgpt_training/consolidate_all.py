"""
Consolidate all training files into ONE master file
For ChatGPT single-upload
"""
import os

ROOT = r"C:\Claude\AI_\chatgpt_training"
OUTPUT = r"C:\Claude\AI_\GURU_JI_MASTER_FILE.txt"

# Order of sections
SECTIONS = [
    ("INTRODUCTION", None),
    ("STUDENT PROFILE", "1_my_profile.txt"),
    ("TEACHING STYLE EXAMPLES", "2_teaching_style_examples.txt"),
    ("TOPICS LIST", "3_topics_list.txt"),
    ("SETUP GUIDE", "HOW_TO_SETUP.txt"),
    ("5-YEAR ROADMAP", "NEXT_LEVEL_ROADMAP.txt"),

    # 13 Teachers
    ("TEACHER 01: OS GURU", "01_OS_Teacher/instructions.txt"),
    ("TEACHER 02: NETWORKS GURU", "02_Networks_Teacher/instructions.txt"),
    ("TEACHER 03: MERN MAHA-GURU", "03_MERN_Teacher/ULTIMATE_instructions.txt"),
    ("MERN: CODE TEACHING SAMPLES", "03_MERN_Teacher/code_teaching_samples.txt"),
    ("MERN: INDUSTRY SECRETS", "03_MERN_Teacher/industry_secrets.txt"),
    ("MERN: INTERVIEW Q&A BANK", "03_MERN_Teacher/interview_qa_bank.txt"),
    ("TEACHER 04: AI GURU", "04_AI_Teacher/instructions.txt"),
    ("TEACHER 05: NLP GURU", "05_NLP_Teacher/instructions.txt"),
    ("TEACHER 06: DBMS GURU", "06_DBMS_Teacher/instructions.txt"),
    ("TEACHER 07: AI AGENTS EXPERT", "07_AI_Agents_Expert/instructions.txt"),
    ("TEACHER 08: GENAI BUILDER", "08_GenAI_Builder/instructions.txt"),
    ("TEACHER 09: CLOUD DEVOPS MASTER", "09_Cloud_DevOps_Master/instructions.txt"),
    ("TEACHER 10: STARTUP FOUNDER MENTOR", "10_Startup_Founder_Mentor/instructions.txt"),
    ("TEACHER 11: SYSTEM DESIGN SENIOR", "11_System_Design_Senior/instructions.txt"),
    ("TEACHER 12: PYTHON MAHA-GURU", "12_Python_Maha_Guru/instructions.txt"),
    ("TEACHER 13: PERSONAL BRAND COACH", "13_Personal_Brand_Coach/instructions.txt"),

    # Power Upgrades
    ("POWER UPGRADE 1: CUSTOM COMMANDS", "POWER_UPGRADES/1_custom_commands.txt"),
    ("POWER UPGRADE 2: ANTI-HALLUCINATION", "POWER_UPGRADES/2_anti_hallucination_guard.txt"),
    ("POWER UPGRADE 3: DAILY ROUTINE", "POWER_UPGRADES/3_daily_routine_template.txt"),
    ("POWER UPGRADE 4: LEARNING TRACKER", "POWER_UPGRADES/4_learning_tracker.txt"),
    ("POWER UPGRADE 5: PROMPT PATTERNS", "POWER_UPGRADES/5_power_prompt_patterns.txt"),
    ("UPGRADE USAGE GUIDE", "POWER_UPGRADES/HOW_TO_USE_UPGRADES.txt"),
]

INTRO = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║       GURU JI'S MASTER TRAINING FILE                         ║
║       ByteFlow Tech — Complete ChatGPT Training Bundle       ║
║       Created: June 2026                                     ║
║       Owner: bantikevat199@gmail.com                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

WHAT IS THIS FILE?
────────────────────────────────────────────────────────────────
This is the CONSOLIDATED master file containing ALL ChatGPT
training material in ONE place. Upload this single file to your
ChatGPT project and ChatGPT will have access to:

✓ 13 Specialist Teachers (OS, Networks, MERN, AI, NLP, DBMS,
  AI Agents, GenAI Builder, Cloud DevOps, Startup Founder,
  System Design, Python, Personal Brand)
✓ 5 Power Upgrades (Custom Commands, Anti-Hallucination,
  Daily Routine, Learning Tracker, Prompt Patterns)
✓ Student Profile + Teaching Style Examples + 5-Year Roadmap

HOW TO USE
────────────────────────────────────────────────────────────────
OPTION A: Single Project Mode (Easier)
- Upload this ONE file to a ChatGPT project
- Use instructions for ANY teacher by saying:
  "Act as [Teacher Name] — and teach [topic]"

OPTION B: Multi-Project Mode (Advanced)
- Create 13 separate ChatGPT projects (one per teacher)
- Upload this file to each project
- ChatGPT will pick relevant section

NAVIGATION
────────────────────────────────────────────────────────────────
Use Ctrl+F to find sections:
- "TEACHER 01" through "TEACHER 13"
- "POWER UPGRADE 1" through "POWER UPGRADE 5"
- "STUDENT PROFILE"
- "5-YEAR ROADMAP"

QUICK COMMAND TO ACTIVATE
────────────────────────────────────────────────────────────────
After uploading, paste this in chat:

"You are Guru Ji's complete AI mentor system. You have access
to 13 specialist teachers + 5 power upgrades. When user asks
about a topic, activate the relevant teacher persona. Use
Hinglish style. Apply 15-step deep dive flow. Wait for NEXT.
Read STUDENT PROFILE section to understand the user (Guru ji,
ByteFlow Tech founder, MERN dev, M.Tech AI student).

Confirm setup by listing all 13 teachers + 5 upgrades you
have access to."

────────────────────────────────────────────────────────────────
"""

def read_file(path):
    full_path = os.path.join(ROOT, path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[Could not read file: {e}]"

with open(OUTPUT, 'w', encoding='utf-8') as out:
    out.write(INTRO)

    for title, filepath in SECTIONS:
        out.write("\n\n")
        out.write("=" * 70 + "\n")
        out.write(f"  {title}\n")
        out.write("=" * 70 + "\n\n")

        if filepath is None:
            continue

        content = read_file(filepath)
        out.write(content)
        out.write("\n")

# Show summary
print(f"Master file created: {OUTPUT}")
size = os.path.getsize(OUTPUT)
print(f"Size: {size:,} bytes ({size/1024:.1f} KB)")
with open(OUTPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    chars = sum(len(l) for l in lines)
print(f"Lines: {len(lines):,}")
print(f"Characters: {chars:,}")
