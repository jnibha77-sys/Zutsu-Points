import os
import requests
from PIL import Image, ImageDraw, ImageFont

# --- Configuration ---
IMAGE_PATH = "zutsu_cs_pt3x.png"
OUTPUT_PATH = "output_scoreboard.png"
LOGO_DIR = "logos"       # Folder containing team logos as tag.png

# ============================================================
# THREE INPUTS — change these to control all 12 teams at once
# ============================================================
LOGO_SIZE = 20    # logo width & height (square) for all teams
NAME_FS   = 11    # team-name font size for all teams
NUM_FS    = 18    # numbers font size for all teams

# Google Sheets API config
API_KEY = "AIzaSyCQsWb6Q1iAu4A9wcrA_oZKrJlzkGEs1NY"
SHEET_ID = "1XXQHJDiAoM0JPQGjVxrctFJNfCOrH0a-PC1wefCc9Q8"
RANGE = "RANKING!A5:K16"  # Rows 5–16 contain the 12 teams

# Column indices in the sheet row (0-based)
# A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10
COL_TEAM_NAME = 3    # Column D
COL_LOGO_TAG = 4     # Column E  (used as logos/tag.png)
COL_MP = 5           # Column F
COL_BOOYAH = 6       # Column G
COL_ELIMS = 7        # Column H
COL_PLACE_PTS = 8    # Column I
COL_TOTAL = 10       # Column K

# --- Font Setup (Chakra Petch) ---
FONT_PATH = "ChakraPetch-Medium2.ttf"
FONT_BOLD_PATH = "ChakraPetch-Bold.ttf"
FONT_SIZE = 18

try:
    font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)
    font_bold = ImageFont.truetype(FONT_BOLD_PATH, size=FONT_SIZE)
except OSError:
    print(f"[WARNING] Could not load Chakra Petch fonts. Falling back to default.")
    font = ImageFont.load_default()
    font_bold = font

# Font cache for per-team sizes (populated on demand)
_font_cache = {}
_font_bold_cache = {}

def get_font(size):
    if size not in _font_cache:
        try:
            _font_cache[size] = ImageFont.truetype(FONT_PATH, size=size)
        except OSError:
            _font_cache[size] = font
    return _font_cache[size]

def get_font_bold(size):
    if size not in _font_bold_cache:
        try:
            _font_bold_cache[size] = ImageFont.truetype(FONT_BOLD_PATH, size=size)
        except OSError:
            _font_bold_cache[size] = font_bold
    return _font_bold_cache[size]

# --- Coordinates ---
# logo_size, name_fs, num_fs are now driven by SIZE_SCALE (see top of file).
team_positions = [
    # Team 1 — large card top-left
    {"logo": (40, 116), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (49, 116), "mp": (230, 265), "booyah": (290, 265), "elims": (345, 265), "place": (385, 265), "total": (420, 265)},
    # Team 2 — left row
    {"logo": (65, 298), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (105, 300), "mp": (230, 300), "booyah": (290, 300), "elims": (345, 300), "place": (385, 300), "total": (420, 300)},
    # Team 3
    {"logo": (65, 333), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (105, 335), "mp": (230, 335), "booyah": (290, 335), "elims": (345, 335), "place": (385, 335), "total": (420, 335)},
    # Team 4
    {"logo": (65, 368), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (105, 370), "mp": (230, 370), "booyah": (290, 370), "elims": (345, 370), "place": (385, 370), "total": (420, 370)},
    # Team 5
    {"logo": (65, 403), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (105, 405), "mp": (230, 405), "booyah": (290, 405), "elims": (345, 405), "place": (385, 405), "total": (420, 405)},
    # Team 6 — right side rows
    {"logo": (510, 148), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 150), "mp": (652, 150), "booyah": (702, 150), "elims": (745, 150), "place": (785, 150), "total": (830, 150)},
    # Team 7
    {"logo": (510, 183), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 185), "mp": (652, 185), "booyah": (702, 185), "elims": (745, 185), "place": (785, 185), "total": (830, 185)},
    # Team 8
    {"logo": (510, 218), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 220), "mp": (652, 220), "booyah": (702, 220), "elims": (745, 220), "place": (785, 220), "total": (830, 220)},
    # Team 9
    {"logo": (510, 253), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 255), "mp": (652, 255), "booyah": (702, 255), "elims": (745, 255), "place": (785, 255), "total": (830, 255)},
    # Team 10
    {"logo": (510, 288), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 290), "mp": (652, 290), "booyah": (702, 290), "elims": (745, 290), "place": (785, 290), "total": (830, 290)},
    # Team 11
    {"logo": (510, 323), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 325), "mp": (652, 325), "booyah": (702, 325), "elims": (745, 325), "place": (785, 325), "total": (830, 325)},
    # Team 12
    {"logo": (510, 358), "logo_size": LOGO_SIZE, "name_fs": NAME_FS, "num_fs": NUM_FS, "name": (545, 360), "mp": (652, 360), "booyah": (702, 360), "elims": (745, 360), "place": (785, 360), "total": (830, 360)},
]


def fetch_sheet_data():
    """Fetch team data from Google Sheets via GAPI REST API."""
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{RANGE}?key={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    rows = data.get("values", [])

    teams = []
    for row in rows:
        # Pad row to at least 11 columns in case of trailing empty cells
        padded = row + [""] * (11 - len(row))
        teams.append({
            "name":     padded[COL_TEAM_NAME],
            "logo_tag": padded[COL_LOGO_TAG],   # e.g. "UGxGRP" -> logos/UGxGRP.png
            "mp":       padded[COL_MP],
            "booyah":   padded[COL_BOOYAH],
            "elims":    padded[COL_ELIMS],
            "place":    padded[COL_PLACE_PTS],
            "total":    padded[COL_TOTAL],
        })
    return teams


def draw_team(img, draw, pos, rank, team, text_color="black"):
    """Draw one team's logo and data at the specified coordinate positions."""
    # --- Paste the team logo ---
    tag = team.get("logo_tag", "").strip()
    if tag:
        logo_path = os.path.join(LOGO_DIR, f"{tag}.png")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")
            s = pos.get("logo_size", LOGO_SIZE)
            logo = logo.resize((s, s), Image.LANCZOS)
            # Paste with alpha mask so transparency is preserved
            img.paste(logo, pos["logo"], logo)
        else:
            print(f"  [WARN] Logo not found: {logo_path}")

    # --- Draw text fields ---
    nf = get_font_bold(pos.get("name_fs", FONT_SIZE))       # team name font
    nf_num = get_font(pos.get("num_fs", FONT_SIZE))         # numbers font
    nf_num_b = get_font_bold(pos.get("num_fs", FONT_SIZE))  # numbers bold (total)
    draw.text(pos["name"],   team["name"],    fill=text_color, font=nf)
    draw.text(pos["mp"],     team["mp"],      fill=text_color, font=nf_num)
    draw.text(pos["booyah"], team["booyah"],  fill=text_color, font=nf_num)
    draw.text(pos["elims"],  team["elims"],   fill=text_color, font=nf_num)
    draw.text(pos["place"],  team["place"],   fill=text_color, font=nf_num)
    draw.text(pos["total"],  team["total"],   fill=text_color, font=nf_num_b)


def main():
    # Fetch live data from Google Sheets
    print(f"Using LOGO_SIZE={LOGO_SIZE}, NAME_FS={NAME_FS}, NUM_FS={NUM_FS}")
    print("Fetching data from Google Sheets...")
    teams = fetch_sheet_data()
    print(f"Loaded {len(teams)} teams.")

    # Open the template image
    img = Image.open(IMAGE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Draw each team at its designated coordinates
    for i, team in enumerate(teams):
        if i >= len(team_positions):
            break
        draw_team(img, draw, team_positions[i], i + 1, team)

    # Save the output
    img.save(OUTPUT_PATH)
    print(f"Scoreboard saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
