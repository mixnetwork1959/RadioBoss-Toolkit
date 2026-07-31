# ==========================================
# Broadcast Scheduler
# Version 4.5.0
# website_generator.py
# ==========================================

from __future__ import annotations

import html
import json
import webbrowser
from datetime import timedelta
from pathlib import Path

from config import (
    get_default_export_directory,
    load_settings
)
from database import Database
from scheduler_controller import SchedulerController
from public_calendar_config import PublicCalendarConfig
from public_calendar_engine import PublicCalendarEngine

class PublicCalendarWebsiteGenerator:

    def __init__(
        self,
        station_name="Radio Albena",
        station_tagline="The Sound of the Black Sea Coast",
        config_filename="public_calendar.json",
        timezone_name="Europe/Sofia",
    ):
        self.station_name = station_name
        self.station_tagline = station_tagline
        self.config_filename = config_filename
        self.timezone_name = timezone_name

    def generate(
        self,
        open_browser=True,
        output_directory=None
    ):
        settings = load_settings()
        events = Database(settings).load_events()
        runtimes = SchedulerController(events).refresh()

        public_config = PublicCalendarConfig(
            self.config_filename
        )
        public_config.load()

        blocks = PublicCalendarEngine().detect(
            runtimes,
            public_config
        )

        programs = []

        for block in blocks:
            duration_minutes = int(
                (block.end - block.start).total_seconds() // 60
            )

            # Exclude invalid and artificial nearly-all-day
            # technical blocks.
            if (
                duration_minutes <= 0
                or duration_minutes >= 18 * 60
            ):
                continue

            common_data = {
                "event_id": block.event_id,
                "title": block.public_name,
                "description": block.description,
                "color": block.color,
            }

            # Normal block: starts and ends on the same day.
            if block.end.date() == block.start.date():
                programs.append(
                    {
                        **common_data,
                        "start": block.start.isoformat(),
                        "end": block.end.isoformat(),
                        "day": block.start.strftime("%A"),
                        "start_time": block.start.strftime("%H:%M"),
                        "end_time": block.end.strftime("%H:%M"),
                    }
                )
                continue

            # Overnight block: split at midnight so it appears in
            # both day columns of the weekly calendar.
            midnight = (
                block.start.replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                )
                + timedelta(days=1)
            )

            # First part: start day until 24:00.
            programs.append(
                {
                    **common_data,
                    "start": block.start.isoformat(),
                    "end": midnight.isoformat(),
                    "day": block.start.strftime("%A"),
                    "start_time": block.start.strftime("%H:%M"),
                    "end_time": "24:00",
                }
            )

            # Second part: next day from 00:00 until the actual end.
            programs.append(
                {
                    **common_data,
                    "start": midnight.isoformat(),
                    "end": block.end.isoformat(),
                    "day": block.end.strftime("%A"),
                    "start_time": "00:00",
                    "end_time": block.end.strftime("%H:%M"),
                }
            )

        week_label = "No programs selected"

        if programs:
            visible_starts = [
                block.start
                for block in blocks
                if int(
                    (block.end - block.start).total_seconds() // 60
                ) > 0
                and int(
                    (block.end - block.start).total_seconds() // 60
                ) < 18 * 60
            ]

            visible_ends = [
                block.end
                for block in blocks
                if int(
                    (block.end - block.start).total_seconds() // 60
                ) > 0
                and int(
                    (block.end - block.start).total_seconds() // 60
                ) < 18 * 60
            ]

            if visible_starts and visible_ends:
                start = min(visible_starts)
                end = max(visible_ends)

                week_label = (
                    f"{start.strftime('%b')} {start.day} – "
                    f"{end.strftime('%b')} {end.day}, {end.year}"
                )

        document = self._document(
            programs=programs,
            week_label=week_label,
        )

        configured_directory = settings.get(
            "export_directory",
            ""
        )

        if output_directory:
            export_directory = Path(output_directory)
        elif configured_directory:
            export_directory = Path(configured_directory)
        else:
            export_directory = get_default_export_directory()

        export_directory = export_directory.expanduser()
        output_file = export_directory / "index.html"

        export_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            document,
            encoding="utf-8"
        )

        if open_browser:
            webbrowser.open(
                output_file.resolve().as_uri()
            )

        return output_file

    def _document(self, programs, week_label):
        station_name = html.escape(self.station_name)
        station_tagline = html.escape(self.station_tagline)
        week_label = html.escape(week_label)
        timezone_name = html.escape(self.timezone_name)
        programs_json = json.dumps(programs, ensure_ascii=False).replace("</", "<\\/")

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{station_name} – Weekly Music Program</title>
<style>
:root {{
  --bg:#07111f; --panel:#0d1828; --border:#283850; --text:#f8fafc;
  --muted:#aebbd0; --accent:#ff8a00; --hour-height:72px; --time-width:72px;
}}
* {{ box-sizing:border-box; }}
html {{ color-scheme:dark; }}
body {{ margin:0; min-height:100vh; background:radial-gradient(circle at top,#14243d 0,#07111f 46%); color:var(--text); font-family:Inter,"Segoe UI",Arial,sans-serif; }}
.app {{ width:min(1850px,100%); margin:0 auto; padding:24px; }}
.topbar {{ display:flex; align-items:center; justify-content:space-between; gap:24px; padding-bottom:18px; border-bottom:1px solid var(--border); }}
.brand {{ display:flex; align-items:center; gap:14px; }}
.brand-icon {{ display:grid; width:48px; height:48px; place-items:center; border:1px solid #345174; border-radius:50%; background:#0e2038; font-size:23px; }}
.brand h1 {{ margin:0; font-size:clamp(1.35rem,2vw,2rem); }}
.brand p {{ margin:4px 0 0; color:var(--muted); }}
.week-label {{ padding:11px 16px; border:1px solid var(--border); border-radius:9px; background:var(--panel); font-weight:700; }}
.toolbar {{ display:flex; align-items:center; justify-content:space-between; gap:18px; padding:18px 0 14px; }}
.eyebrow {{ margin-bottom:4px; color:#78bfff; font-size:.78rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase; }}
.toolbar h2 {{ margin:0; font-size:1.2rem; }}
.now-playing {{ display:flex; align-items:center; gap:10px; min-width:260px; padding:10px 14px; border:1px solid #a14c16; border-radius:9px; background:#2a160c; }}
.now-playing small,.now-playing strong,.now-playing span {{ display:block; }}
.now-playing small {{ color:#ffb06a; font-size:.68rem; font-weight:900; letter-spacing:.12em; }}
.now-playing #now-time {{ margin-top:2px; color:#f8c89e; font-size:.78rem; }}
.live-dot {{ width:11px; height:11px; border-radius:50%; background:#ff5a36; animation:pulse 1.8s infinite; }}
@keyframes pulse {{ 0%{{box-shadow:0 0 0 0 rgb(255 90 54 / 65%)}} 70%{{box-shadow:0 0 0 9px rgb(255 90 54 / 0%)}} 100%{{box-shadow:0 0 0 0 rgb(255 90 54 / 0%)}} }}
.message {{ margin-bottom:14px; padding:14px; border:1px solid #805e25; border-radius:9px; background:#3a2a10; color:#ffe5a8; }}
.week-grid {{ position:relative; display:grid; grid-template-columns:var(--time-width) repeat(7,minmax(165px,1fr)); overflow:auto; border:1px solid var(--border); border-radius:12px; background:var(--panel); box-shadow:0 22px 55px rgb(0 0 0 / 24%); }}
.corner,.day-heading {{ position:sticky; top:0; z-index:7; min-height:54px; border-bottom:1px solid var(--border); background:#0a1423; }}
.corner {{ left:0; z-index:9; border-right:1px solid var(--border); }}
.day-heading {{ display:grid; place-items:center; padding:8px; border-right:1px solid var(--border); text-align:center; font-weight:800; }}
.time-column {{ position:sticky; left:0; z-index:5; border-right:1px solid var(--border); background:#0a1423; }}
.time-label {{ height:var(--hour-height); padding:8px 10px; border-bottom:1px solid var(--border); color:#dce7f7; font-size:.82rem; font-weight:700; }}
.day-column {{ position:relative; min-height:calc(var(--hour-height) * 24); border-right:1px solid var(--border); background:repeating-linear-gradient(to bottom,transparent 0,transparent calc(var(--hour-height) - 1px),#293850 calc(var(--hour-height) - 1px),#293850 var(--hour-height)); }}
.program {{ position:absolute; left:5px; right:5px; overflow:hidden; padding:9px; border:1px solid rgb(255 255 255 / 22%); border-radius:8px; box-shadow:inset 0 1px rgb(255 255 255 / 15%),0 4px 12px rgb(0 0 0 / 20%); }}
.program.is-live {{ z-index:4; outline:3px solid var(--accent); outline-offset:-3px; box-shadow:inset 0 1px rgb(255 255 255 / 20%),0 0 0 2px rgb(255 138 0 / 25%),0 0 22px rgb(255 138 0 / 55%); }}
.program-time {{ font-size:.72rem; opacity:.9; }}
.program-title {{ margin-top:5px; font-size:.88rem; font-weight:900; }}
.program-description {{ margin-top:5px; font-size:.73rem; line-height:1.35; opacity:.95; }}
.program-progress {{ position:absolute; right:8px; bottom:8px; left:8px; height:5px; overflow:hidden; border-radius:99px; background:rgb(0 0 0 / 28%); }}
.program-progress > span {{ display:block; width:0; height:100%; border-radius:inherit; background:#fff; transition:width .35s ease; }}
.current-time-line {{ position:absolute; right:0; left:0; z-index:6; height:2px; pointer-events:none; background:#ff3b30; box-shadow:0 0 7px rgb(255 59 48 / 80%); }}
.current-time-line::before {{ position:absolute; top:50%; left:-5px; width:10px; height:10px; border-radius:50%; background:#ff3b30; content:""; transform:translateY(-50%); }}
footer {{ padding:14px 4px 0; color:var(--muted); text-align:center; font-size:.82rem; line-height:1.55; }}
@media(max-width:900px) {{ .app{{padding:14px}} .topbar{{align-items:flex-start;flex-direction:column}} .week-label{{width:100%}} .toolbar{{align-items:stretch;flex-direction:column}} .now-playing{{width:100%}} .week-grid{{overflow-x:auto}} }}
</style>
</head>
<body>
<main class="app">
<header class="topbar">
  <div class="brand"><div class="brand-icon">📻</div><div><h1>{station_name}</h1><p>{station_tagline}</p></div></div>
  <div class="week-label">{week_label}</div>
</header>
<section class="toolbar">
  <div><div class="eyebrow">Public Calendar</div><h2>Weekly Music Program</h2></div>
  <div id="now-playing" class="now-playing" hidden><span class="live-dot"></span><div><small>LIVE NOW</small><strong id="now-title"></strong><span id="now-time"></span></div></div>
</section>
<div id="message" class="message" hidden></div>
<section id="week-view" class="week-grid" aria-label="Weekly music program"></section>
<footer><div>All times shown in {timezone_name}</div><div>Schedule subject to change.</div></footer>
</main>
<script>
const PROGRAMS = {programs_json};
const STATION_TIMEZONE = {json.dumps(self.timezone_name)};
const HOUR_HEIGHT = 72;
const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
function parseDate(v){{return new Date(v)}}
function minutesSinceMidnight(d){{return d.getHours()*60+d.getMinutes()}}
function durationMinutes(s,e){{return Math.max(1,Math.round((e-s)/60000))}}
function escapeHtml(v){{const e=document.createElement("div");e.textContent=v??"";return e.innerHTML}}
function contrastColor(h){{const c=(h||"").replace("#","");if(c.length!==6)return"#fff";const r=parseInt(c.slice(0,2),16),g=parseInt(c.slice(2,4),16),b=parseInt(c.slice(4,6),16);return((r*299+g*587+b*114)/1000)>=145?"#06101f":"#fff"}}
function stationNow(){{const f=new Intl.DateTimeFormat("en-CA",{{timeZone:STATION_TIMEZONE,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",second:"2-digit",hourCycle:"h23"}});const p=Object.fromEntries(f.formatToParts(new Date()).filter(x=>x.type!=="literal").map(x=>[x.type,x.value]));return new Date(+p.year,+p.month-1,+p.day,+p.hour,+p.minute,+p.second)}}
function createTimeColumn(){{const c=document.createElement("div");c.className="time-column";for(let h=0;h<24;h++){{const l=document.createElement("div");l.className="time-label";l.textContent=`${{String(h).padStart(2,"0")}}:00`;c.appendChild(l)}}return c}}
function createProgramCard(p){{const s=parseDate(p.start),e=parseDate(p.end);let ve=e;if(e.getDate()!==s.getDate()){{ve=new Date(s);ve.setHours(24,0,0,0)}}const tm=minutesSinceMidnight(s),hm=durationMinutes(s,ve);const c=document.createElement("article");c.className="program";c.dataset.start=p.start;c.dataset.end=p.end;c.dataset.title=p.title;c.style.top=`${{tm/60*HOUR_HEIGHT}}px`;c.style.height=`${{Math.max(42,hm/60*HOUR_HEIGHT-5)}}px`;const color=p.color||"#4EA3FF";c.style.background=color;c.style.color=contrastColor(color);c.innerHTML=`<div class="program-time">${{p.start_time}} – ${{p.end_time}}</div><div class="program-title">${{escapeHtml(p.title)}}</div>${{p.description?`<div class="program-description">${{escapeHtml(p.description)}}</div>`:""}}<div class="program-progress" hidden><span></span></div>`;return c}}
function buildWeekView(){{const g=document.getElementById("week-view");g.innerHTML="";const corner=document.createElement("div");corner.className="corner";g.appendChild(corner);DAYS.forEach(d=>{{const h=document.createElement("div");h.className="day-heading";h.textContent=d;g.appendChild(h)}});g.appendChild(createTimeColumn());DAYS.forEach(d=>{{const col=document.createElement("div");col.className="day-column";col.dataset.day=d;PROGRAMS.filter(p=>p.day===d).forEach(p=>col.appendChild(createProgramCard(p)));g.appendChild(col)}})}}
function updateLiveState(){{const now=stationNow();const box=document.getElementById("now-playing"),title=document.getElementById("now-title"),time=document.getElementById("now-time");let active=null,as=null,ae=null;document.querySelectorAll(".program").forEach(card=>{{const s=parseDate(card.dataset.start),e=parseDate(card.dataset.end),live=now>=s&&now<e;card.classList.toggle("is-live",live);const pb=card.querySelector(".program-progress"),fill=pb.querySelector("span");if(live){{const pct=Math.max(0,Math.min(100,(now-s)/(e-s)*100));pb.hidden=false;fill.style.width=`${{pct}}%`;active=card;as=s;ae=e}}else{{pb.hidden=true;fill.style.width="0%"}}}});if(active){{box.hidden=false;title.textContent=active.dataset.title;time.textContent=`${{as.toLocaleTimeString([],{{hour:"2-digit",minute:"2-digit"}})}} – ${{ae.toLocaleTimeString([],{{hour:"2-digit",minute:"2-digit"}})}}`}}else box.hidden=true;updateCurrentTimeLine(now)}}
function updateCurrentTimeLine(now){{document.querySelectorAll(".current-time-line").forEach(x=>x.remove());const d=DAYS[(now.getDay()+6)%7],col=document.querySelector(`.day-column[data-day="${{d}}"]`);if(!col)return;const line=document.createElement("div");line.className="current-time-line";line.style.top=`${{minutesSinceMidnight(now)/60*HOUR_HEIGHT}}px`;col.appendChild(line)}}
if(PROGRAMS.length===0){{const m=document.getElementById("message");m.hidden=false;m.textContent="No public music programs have been selected yet."}}
buildWeekView();updateLiveState();setInterval(updateLiveState,30000);
</script>
</body>
</html>'''


def main():
    output = PublicCalendarWebsiteGenerator().generate(open_browser=True)
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
