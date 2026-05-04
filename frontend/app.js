const API_URL = "http://127.0.0.1:8000";

const MONTH_NAMES_UZ = [
  "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
  "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"
];

const elements = {
  authPage: document.getElementById("auth-page"),
  appPage: document.getElementById("app-page"),

  loginUsername: document.getElementById("login-username"),
  loginPassword: document.getElementById("login-password"),
  regUsername: document.getElementById("reg-username"),
  regPassword: document.getElementById("reg-password"),

  loginBtn: document.getElementById("login-btn"),
  registerBtn: document.getElementById("register-btn"),

  logoutBtn: document.getElementById("logout-btn"),
  today: document.getElementById("today"),
  prevMonth: document.getElementById("prev-month"),
  nextMonth: document.getElementById("next-month"),

  notifyBox: document.getElementById("notify-box") || document.querySelector(".notify"),
  notifyBtn: document.getElementById("notify-btn"),
  notifyCount: document.getElementById("notify-count"),
  notifyPopover: document.getElementById("notify-popover"),
  notifyList: document.getElementById("notify-list"),

  grid: document.getElementById("calendar-grid"),
  monthLabel: document.getElementById("month-label"),
  yearLabel: document.getElementById("year-label"),

  selectedDate: document.getElementById("selected-date"),
  selectedSubtitle: document.getElementById("selected-subtitle"),
  status: document.getElementById("status"),
  taskList: document.getElementById("task-list"),

  openAdd: document.getElementById("open-add"),
  createForm: document.getElementById("create-form"),
  cancelAdd: document.getElementById("cancel-add"),
  submitBtn: document.getElementById("submit-btn"),
  title: document.getElementById("title"),
  description: document.getElementById("description"),
};

let viewDate = startOfMonth(new Date());
let selectedDate = stripTime(new Date());
let tasks = [];
let editTaskId = null;

function stripTime(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function startOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function endOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

function addDays(date, days) {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return stripTime(d);
}

function isoDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function parseIsoDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return stripTime(new Date(y, m - 1, d));
}

function sameDay(a, b) {
  return a.getFullYear() === b.getFullYear()
    && a.getMonth() === b.getMonth()
    && a.getDate() === b.getDate();
}

function startOfWeekMonday(date) {
  const d = stripTime(date);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  return addDays(d, diff);
}

function endOfWeekSunday(date) {
  return addDays(startOfWeekMonday(date), 6);
}

function calendarRangeForMonth(date) {
  return {
    start: startOfWeekMonday(startOfMonth(date)),
    end: endOfWeekSunday(endOfMonth(date)),
  };
}

function getISOWeekNumber(date) {
  const d = stripTime(date);
  const day = d.getDay() || 7;
  d.setDate(d.getDate() + 4 - day);
  const yearStart = new Date(d.getFullYear(), 0, 1);
  const diffDays = Math.floor((d - yearStart) / 86400000) + 1;
  return Math.ceil(diffDays / 7);
}

function formatLongDate(date) {
  return new Intl.DateTimeFormat("uz-UZ", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

function escapeHtml(text) {
  return (text ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function getToken() {
  return localStorage.getItem("token");
}

function setAuthView() {
  elements.authPage.classList.remove("hidden");
  elements.appPage.classList.add("hidden");

  elements.logoutBtn.classList.add("hidden");
  elements.today.classList.add("hidden");
  elements.prevMonth.classList.add("hidden");
  elements.nextMonth.classList.add("hidden");
  if (elements.notifyBox) elements.notifyBox.classList.add("hidden");
  elements.notifyPopover.classList.add("hidden");

  elements.yearLabel.textContent = "";
  elements.monthLabel.textContent = "Login";
}

function setAppView() {
  elements.authPage.classList.add("hidden");
  elements.appPage.classList.remove("hidden");

  elements.logoutBtn.classList.remove("hidden");
  elements.today.classList.remove("hidden");
  elements.prevMonth.classList.remove("hidden");
  elements.nextMonth.classList.remove("hidden");
  if (elements.notifyBox) elements.notifyBox.classList.remove("hidden");
  elements.notifyPopover.classList.add("hidden");
}

function showAppByAuth() {
  if (getToken()) {
    setAppView();
    refresh();
  } else {
    setAuthView();
  }
}

async function apiRequest(path, options = {}) {
  const token = getToken();

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("token");
      setAuthView();
    }

    throw new Error(data?.detail || `Xatolik: ${response.status}`);
  }

  return data;
}

function normalizeTask(task) {
  return {
    id: task.id,
    title: task.title,
    description: task.description,
    due_date: task.due_date,
    completed: task.is_done,
  };
}

async function register() {
  try {
    await apiRequest("/register", {
      method: "POST",
      body: JSON.stringify({
        username: elements.regUsername.value,
        password: elements.regPassword.value,
      }),
    });

    alert("Register bo‘ldi. Endi login qiling.");

    elements.loginUsername.value = elements.regUsername.value;
    elements.regUsername.value = "";
    elements.regPassword.value = "";
  } catch (err) {
    alert(err.message);
  }
}

async function login() {
  try {
    const formData = new URLSearchParams();
    formData.append("username", elements.loginUsername.value);
    formData.append("password", elements.loginPassword.value);

    const response = await fetch(`${API_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login xato");
    }

    localStorage.setItem("token", data.access_token);

    elements.loginUsername.value = "";
    elements.loginPassword.value = "";

    setAppView();
    refresh();
  } catch (err) {
    alert(err.message);
  }
}

function logout() {
  localStorage.removeItem("token");
  tasks = [];
  closeForm();
  setAuthView();
}

async function getTasksFromApi(startDate, endDate) {
  const data = await apiRequest(
    `/tasks?start_date=${isoDate(startDate)}&end_date=${isoDate(endDate)}`
  );

  return data.map(normalizeTask);
}

async function createTask(payload) {
  return apiRequest("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

async function updateTask(taskId, patch) {
  const backendPatch = {};

  if ("title" in patch) backendPatch.title = patch.title;
  if ("description" in patch) backendPatch.description = patch.description;
  if ("due_date" in patch) backendPatch.due_date = patch.due_date;
  if ("completed" in patch) backendPatch.is_done = patch.completed;

  return apiRequest(`/tasks/${taskId}`, {
    method: "PUT",
    body: JSON.stringify(backendPatch),
  });
}

async function deleteTask(taskId) {
  return apiRequest(`/tasks/${taskId}`, {
    method: "DELETE",
  });
}

function getTasksForDate(date) {
  const key = isoDate(date);
  return tasks.filter((task) => task.due_date === key);
}

function getNext5DaysTasks() {
  const today = stripTime(new Date());
  const end = addDays(today, 5);

  return tasks.filter((task) => {
    if (!task.due_date) return false;
    if (task.completed) return false;
    const taskDate = parseIsoDate(task.due_date);
    return taskDate >= today && taskDate <= end;
  });
}

function renderNotifications() {
  const upcoming = getNext5DaysTasks();

  elements.notifyCount.textContent = String(upcoming.length);
  elements.notifyCount.classList.toggle("hidden", upcoming.length === 0);

  if (!upcoming.length) {
    elements.notifyList.innerHTML = `<li class="notify-empty">Keyingi 5 kunda task yo‘q.</li>`;
    return;
  }

  elements.notifyList.innerHTML = upcoming
    .map((task) => {
      const date = parseIsoDate(task.due_date);
      const titleClass = task.completed ? "notify-task done" : "notify-task";

      return `
        <li class="notify-item" data-date="${task.due_date}">
          <div class="notify-date">${date.getDate()} ${MONTH_NAMES_UZ[date.getMonth()]}</div>
          <p class="${titleClass}">${escapeHtml(task.title)}</p>
        </li>
      `;
    })
    .join("");
}

function renderCalendar() {
  elements.yearLabel.textContent = viewDate.getFullYear();
  elements.monthLabel.textContent = MONTH_NAMES_UZ[viewDate.getMonth()];

  const range = calendarRangeForMonth(viewDate);
  const today = stripTime(new Date());
  const rows = [];

  for (let weekStart = range.start; weekStart <= range.end; weekStart = addDays(weekStart, 7)) {
    const weekNum = getISOWeekNumber(weekStart);
    const cells = [`<div class="week-num">${weekNum}</div>`];

    for (let i = 0; i < 7; i++) {
      const d = addDays(weekStart, i);
      const key = isoDate(d);
      const dayTasks = tasks.filter((task) => task.due_date === key);
      const preview = dayTasks.slice(0, 3);

      const pills = preview.map((task) => {
        const cls = task.completed ? "task-pill done" : "task-pill";
        return `<div class="${cls}">${escapeHtml(task.title)}</div>`;
      }).join("");

      const more = dayTasks.length > 3
        ? `<div class="more">+${dayTasks.length - 3} more</div>`
        : "";

      const classes = [
        "day",
        d.getMonth() !== viewDate.getMonth() ? "other-month" : "",
        sameDay(d, selectedDate) ? "selected" : "",
        sameDay(d, today) ? "today" : "",
      ].filter(Boolean).join(" ");

      const isWeekend = d.getDay() === 0 || d.getDay() === 6;
      const dayNumberClass = isWeekend ? "day-number weekend" : "day-number";

      cells.push(`
        <div class="${classes}" data-date="${key}">
          <div class="${dayNumberClass}">${d.getDate()}</div>
          <div class="day-tasks">${pills}${more}</div>
          <button class="day-add" type="button">+</button>
        </div>
      `);
    }

    rows.push(`<div class="week-row">${cells.join("")}</div>`);
  }

  elements.grid.innerHTML = rows.join("");
}

function renderPanel() {
  const selectedTasks = getTasksForDate(selectedDate);

  elements.selectedDate.textContent = formatLongDate(selectedDate);
  elements.selectedSubtitle.textContent = selectedTasks.length
    ? `${selectedTasks.length} ta task`
    : "Task yo‘q";

  if (!selectedTasks.length) {
    elements.taskList.innerHTML = `<li class="status">Hozircha task yo‘q.</li>`;
    return;
  }

  elements.taskList.innerHTML = selectedTasks.map((task) => {
    const titleClass = task.completed ? "task-title done" : "task-title";
    const desc = task.description
      ? `<p class="task-desc">${escapeHtml(task.description)}</p>`
      : "";

    return `
      <li class="task-item" data-id="${task.id}">
        <input class="toggle" type="checkbox" ${task.completed ? "checked" : ""} />
        <div>
          <p class="${titleClass}">${escapeHtml(task.title)}</p>
          ${desc}
        </div>
        <div class="task-actions">
          <button class="icon-btn edit" type="button">Edit</button>
          <button class="icon-btn danger delete" type="button">Delete</button>
        </div>
      </li>
    `;
  }).join("");
}

function renderAll() {
  renderCalendar();
  renderPanel();
  renderNotifications();
}

async function refresh() {
  try {
    elements.status.textContent = "Yuklanyapti...";

    const range = calendarRangeForMonth(viewDate);
    const today = stripTime(new Date());
    const upcomingEnd = addDays(today, 5);

    const calendarTasks = await getTasksFromApi(range.start, range.end);
    const upcomingTasks = await getTasksFromApi(today, upcomingEnd);

    const map = new Map();

    for (const task of calendarTasks) map.set(task.id, task);
    for (const task of upcomingTasks) map.set(task.id, task);

    tasks = Array.from(map.values());

    renderAll();
    elements.status.textContent = "";
  } catch (err) {
    elements.status.textContent = `Xatolik: ${err.message}`;
  }
}

function openCreateForm() {
  editTaskId = null;
  elements.submitBtn.textContent = "Saqlash";
  elements.title.value = "";
  elements.description.value = "";
  elements.createForm.classList.remove("hidden");
  elements.title.focus();
}

function openEditForm(task) {
  editTaskId = task.id;
  elements.submitBtn.textContent = "Yangilash";
  elements.title.value = task.title || "";
  elements.description.value = task.description || "";
  elements.createForm.classList.remove("hidden");
  elements.title.focus();
}

function closeForm() {
  editTaskId = null;
  elements.createForm.classList.add("hidden");
  elements.title.value = "";
  elements.description.value = "";
  elements.submitBtn.textContent = "Saqlash";
}

elements.loginBtn.addEventListener("click", login);
elements.registerBtn.addEventListener("click", register);
elements.logoutBtn.addEventListener("click", logout);

elements.notifyBtn.addEventListener("click", (event) => {
  event.stopPropagation();
  elements.notifyPopover.classList.toggle("hidden");
});

elements.notifyPopover.addEventListener("click", (event) => {
  event.stopPropagation();
});

document.addEventListener("click", () => {
  elements.notifyPopover.classList.add("hidden");
});

elements.notifyList.addEventListener("click", (event) => {
  const item = event.target.closest(".notify-item");
  if (!item) return;

  selectedDate = parseIsoDate(item.dataset.date);
  viewDate = startOfMonth(selectedDate);
  elements.notifyPopover.classList.add("hidden");

  refresh();
});

elements.prevMonth.addEventListener("click", () => {
  viewDate = startOfMonth(new Date(viewDate.getFullYear(), viewDate.getMonth() - 1, 1));
  selectedDate = startOfMonth(viewDate);
  closeForm();
  refresh();
});

elements.nextMonth.addEventListener("click", () => {
  viewDate = startOfMonth(new Date(viewDate.getFullYear(), viewDate.getMonth() + 1, 1));
  selectedDate = startOfMonth(viewDate);
  closeForm();
  refresh();
});

elements.today.addEventListener("click", () => {
  const now = stripTime(new Date());
  viewDate = startOfMonth(now);
  selectedDate = now;
  closeForm();
  refresh();
});

elements.grid.addEventListener("click", (event) => {
  const dayEl = event.target.closest(".day");
  if (!dayEl) return;

  selectedDate = parseIsoDate(dayEl.dataset.date);

  if (
    selectedDate.getMonth() !== viewDate.getMonth() ||
    selectedDate.getFullYear() !== viewDate.getFullYear()
  ) {
    viewDate = startOfMonth(selectedDate);
    refresh();
  } else {
    renderAll();
  }

  if (event.target.classList.contains("day-add")) {
    openCreateForm();
  }
});

elements.openAdd.addEventListener("click", openCreateForm);
elements.cancelAdd.addEventListener("click", closeForm);

elements.createForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = elements.title.value.trim();
  const description = elements.description.value.trim();

  if (!title) return;

  try {
    elements.status.textContent = editTaskId ? "Yangilanmoqda..." : "Saqlanyapti...";

    if (editTaskId) {
      await updateTask(editTaskId, {
        title,
        description: description || null,
      });
    } else {
      await createTask({
        title,
        description: description || null,
        due_date: isoDate(selectedDate),
      });
    }

    closeForm();
    await refresh();
  } catch (err) {
    elements.status.textContent = `Xatolik: ${err.message}`;
  }
});

elements.taskList.addEventListener("click", async (event) => {
  const item = event.target.closest(".task-item");
  if (!item) return;

  const taskId = Number(item.dataset.id);
  const task = tasks.find((t) => t.id === taskId);

  if (!task) return;

  try {
    if (event.target.classList.contains("toggle")) {
      await updateTask(taskId, {
        completed: event.target.checked,
      });
      await refresh();
    }

    if (event.target.classList.contains("edit")) {
      openEditForm(task);
    }

    if (event.target.classList.contains("delete")) {
      if (!confirm("Task o‘chirilsinmi?")) return;
      await deleteTask(taskId);
      
      await refresh();
    }
  } catch (err) {
    elements.status.textContent = `Xatolik: ${err.message}`;
  }
});

showAppByAuth();
