import json
import logging
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/Upcoming-and-Live-Sports-Data/main/Sports_data.json"
OUTPUT_FILE = "matches.json"

def parse_match_time(start_time_str):
    if not start_time_str:
        return ""
    start_time_str = start_time_str.strip()
    formats = [
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %I:%M %p",
        "%d-%m-%Y %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %I:%M:%S %p",
        "%d/%m/%Y %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(start_time_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
    return start_time_str

def format_stream_link(stream):
    channel_name = stream.get("channel_name") or stream.get("name") or "Stream"
    channel_name = channel_name.strip()
    stream_url = stream.get("stream_url") or stream.get("url") or ""
    stream_url = stream_url.strip()

    if not stream_url:
        return ""

    headers_part = ""

    # Priority 1: ClearKey DRM
    kid = stream.get("kid")
    key = stream.get("key")
    if kid and key:
        headers_part = f"|drmScheme=clearkey&drmLicense={kid.strip()}:{key.strip()}"
    else:
        # Priority 2: Cookie or Referer (User-Agent excluded)
        cookie = stream.get("cookie") or stream.get("Cookie")
        referer = stream.get("referer") or stream.get("Referer")

        if cookie:
            headers_part = f"|Cookie={cookie.strip()}"
        elif referer:
            headers_part = f"|Referer={referer.strip()}"

    return f"{channel_name},,{stream_url}{headers_part}"

def transform_matches(source_data):
    raw_matches = source_data.get("matches", [])
    output_list = []

    for match in raw_matches:
        category = match.get("Category", "").strip()
        event_info = match.get("eventInfo", {}) or {}

        event_name = event_info.get("eventName", "").strip() or match.get("event_name", "").strip()
        if category and event_name:
            event_title = f"{category.upper()} | {event_name}"
        elif event_name:
            event_title = event_name
        elif category:
            event_title = category.upper()
        else:
            event_title = "SPORTS MATCH"

        start_time = event_info.get("startTime", "")
        match_time = parse_match_time(start_time)

        team1_title = event_info.get("teamA", "").strip() or match.get("teamA", "")
        team2_title = event_info.get("teamB", "").strip() or match.get("teamB", "")
        team1_logo = event_info.get("teamAFlag", "").strip()
        team2_logo = event_info.get("teamBFlag", "").strip()

        status = match.get("status", "").strip().upper()
        is_hot = (status == "LIVE")

        streams = match.get("streams", [])
        stream_links = []
        for s in streams:
            formatted_s = format_stream_link(s)
            if formatted_s:
                stream_links.append(formatted_s)

        stream_link_str = ",) ".join(stream_links)

        output_list.append({
            "eventTitle": event_title,
            "matchTime": match_time,
            "team1Logo": team1_logo,
            "team2Logo": team2_logo,
            "team1Title": team1_title,
            "team2Title": team2_title,
            "streamLink": stream_link_str,
            "isHot": is_hot
        })

    return output_list

def main():
    logging.info(f"Fetching sports data from {SOURCE_URL}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(SOURCE_URL, headers=headers, timeout=30)
    resp.raise_for_status()

    source_data = resp.json()
    transformed = transform_matches(source_data)
    logging.info(f"Successfully transformed {len(transformed)} matches.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=4, ensure_ascii=False)
    logging.info(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
