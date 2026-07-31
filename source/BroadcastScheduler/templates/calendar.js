/* ==========================================
   Broadcast Scheduler
   Public Calendar Website
   Version 3.3.0
   ========================================== */

const HOUR_HEIGHT = 72;
const DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
];

function parseLocalDate(value) {
    return new Date(value);
}

function minutesSinceMidnight(date) {
    return (date.getHours() * 60) + date.getMinutes();
}

function durationMinutes(start, end) {
    return Math.max(
        1,
        Math.round((end - start) / 60000)
    );
}

function contrastColor(hexColor) {
    const color = hexColor.replace("#", "");

    if (color.length !== 6) {
        return "#ffffff";
    }

    const red = parseInt(color.slice(0, 2), 16);
    const green = parseInt(color.slice(2, 4), 16);
    const blue = parseInt(color.slice(4, 6), 16);

    const brightness =
        ((red * 299) + (green * 587) + (blue * 114))
        / 1000;

    return brightness >= 145
        ? "#06101f"
        : "#ffffff";
}

function createTimeColumn() {
    const column = document.createElement("div");
    column.className = "schedule-time-column";

    for (let hour = 0; hour < 24; hour += 1) {
        const label = document.createElement("div");
        label.className = "schedule-time-label";
        label.textContent =
            `${String(hour).padStart(2, "0")}:00`;

        column.appendChild(label);
    }

    return column;
}

function buildWeekView(programs) {
    const grid = document.getElementById(
        "schedule-week-view"
    );

    grid.innerHTML = "";

    const corner = document.createElement("div");
    corner.className = "schedule-corner";
    grid.appendChild(corner);

    DAY_NAMES.forEach((dayName) => {
        const heading = document.createElement("div");
        heading.className = "schedule-day-heading";
        heading.textContent = dayName;
        grid.appendChild(heading);
    });

    grid.appendChild(createTimeColumn());

    DAY_NAMES.forEach((dayName) => {
        const column = document.createElement("div");
        column.className = "schedule-day-column";
        column.dataset.day = dayName;

        const dayPrograms = programs.filter(
            (program) => program.day === dayName
        );

        dayPrograms.forEach((program) => {
            const start = parseLocalDate(program.start);
            const end = parseLocalDate(program.end);

            let visibleEnd = end;

            if (end.getDate() !== start.getDate()) {
                visibleEnd = new Date(start);
                visibleEnd.setHours(24, 0, 0, 0);
            }

            const topMinutes = minutesSinceMidnight(start);
            const heightMinutes = durationMinutes(
                start,
                visibleEnd
            );

            const card = document.createElement("article");
            card.className = "schedule-program";
            card.style.top =
                `${(topMinutes / 60) * HOUR_HEIGHT}px`;
            card.style.height =
                `${Math.max(42, (heightMinutes / 60) * HOUR_HEIGHT - 4)}px`;
            card.style.background = program.color;
            card.style.color = contrastColor(program.color);

            card.innerHTML = `
                <div class="schedule-program-time">
                    ${program.start_time} – ${program.end_time}
                </div>
                <div class="schedule-program-title">
                    ${escapeHtml(program.title)}
                </div>
                ${
                    program.description
                        ? `<div class="schedule-program-description">
                            ${escapeHtml(program.description)}
                           </div>`
                        : ""
                }
            `;

            column.appendChild(card);
        });

        grid.appendChild(column);
    });
}

function buildDayView(programs) {
    const container = document.getElementById(
        "schedule-day-view"
    );

    container.innerHTML = "";

    DAY_NAMES.forEach((dayName) => {
        const dayPrograms = programs.filter(
            (program) => program.day === dayName
        );

        if (dayPrograms.length === 0) {
            return;
        }

        const section = document.createElement("section");
        section.className = "schedule-day-section";

        const heading = document.createElement("h2");
        heading.textContent = dayName;
        section.appendChild(heading);

        dayPrograms.forEach((program) => {
            const card = document.createElement("article");
            card.className = "schedule-day-card";
            card.style.background = program.color;
            card.style.color = contrastColor(program.color);

            card.innerHTML = `
                <div class="schedule-day-card-time">
                    ${program.start_time} – ${program.end_time}
                </div>
                <div class="schedule-day-card-title">
                    ${escapeHtml(program.title)}
                </div>
                ${
                    program.description
                        ? `<div class="schedule-day-card-description">
                            ${escapeHtml(program.description)}
                           </div>`
                        : ""
                }
            `;

            section.appendChild(card);
        });

        container.appendChild(section);
    });
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function activateView(viewName) {
    const weekView = document.getElementById(
        "schedule-week-view"
    );

    const dayView = document.getElementById(
        "schedule-day-view"
    );

    const buttons = document.querySelectorAll(
        ".view-button"
    );

    buttons.forEach((button) => {
        button.classList.toggle(
            "active",
            button.dataset.view === viewName
        );
    });

    if (viewName === "day") {
        weekView.hidden = true;
        dayView.hidden = false;
    } else {
        weekView.hidden = false;
        dayView.hidden = true;
    }
}

async function loadSchedule() {
    const message = document.getElementById(
        "schedule-message"
    );

    try {
        const response = await fetch(
            "public_schedule.json",
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data = await response.json();
        const programs = data.programs ?? [];

        buildWeekView(programs);
        buildDayView(programs);

        if (programs.length === 0) {
            message.hidden = false;
            message.textContent =
                "No public music programs have been selected yet.";
        }
    } catch (error) {
        message.hidden = false;
        message.textContent =
            "The schedule data could not be loaded. " +
            "Open this page through a web server or upload all output files together.";

        console.error(error);
    }
}

document.querySelectorAll(
    ".view-button"
).forEach((button) => {
    button.addEventListener("click", () => {
        activateView(button.dataset.view);
    });
});

loadSchedule();
