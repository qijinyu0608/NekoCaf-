async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (response.status === 204) {
    return { ok: true, payload: null };
  }

  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }

  return { ok: response.ok, payload, status: response.status };
}

async function loginAs(persona) {
  return requestJson("/api/session/login", {
    method: "POST",
    body: JSON.stringify({ persona }),
  });
}

async function logoutCurrentSession() {
  return requestJson("/api/session/logout", { method: "POST" });
}

function bindSessionButtons() {
  document.querySelectorAll("[data-login-persona]").forEach((button) => {
    button.addEventListener("click", async () => {
      const persona = button.getAttribute("data-login-persona");
      if (!persona) return;
      await loginAs(persona);
      window.location.reload();
    });
  });

  document.querySelectorAll("[data-logout]").forEach((button) => {
    button.addEventListener("click", async () => {
      await logoutCurrentSession();
      window.location.href = "/";
    });
  });
}

function bindStaffActions() {
  document.querySelectorAll("[data-checkin-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const reservationId = button.getAttribute("data-checkin-id");
      if (!reservationId) return;
      await requestJson(`/api/staff/reservations/${reservationId}/check-in`, {
        method: "POST",
      });
      window.location.reload();
    });
  });
}

function bindBookingForm() {
  const form = document.querySelector("#booking-form");
  if (!form) return;

  const slotList = document.querySelector("#slot-list");
  const submitButton = document.querySelector("#booking-submit");
  const message = document.querySelector("#booking-message");
  const storeSelect = document.querySelector("#store-select");
  const dateInput = document.querySelector("#date-input");
  const partySizeSelect = document.querySelector("#party-size-select");

  let selectedSlotId = slotList?.querySelector(".slot-pill.selected")?.getAttribute("data-slot-id") || "";

  function renderSlots(slots) {
    if (!slotList) return;
    slotList.innerHTML = "";

    if (!slots.length) {
      slotList.innerHTML = '<p class="metric-note">当前条件暂无可预约时段。</p>';
      selectedSlotId = "";
      return;
    }

    slots.forEach((slot, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `slot-pill ${index === 0 ? "selected" : ""}`;
      button.dataset.slotId = slot.slotId;
      button.innerHTML = `<strong>${slot.startAt.slice(11, 16)}</strong><span>${slot.zoneName}</span>`;
      button.addEventListener("click", () => {
        slotList.querySelectorAll(".slot-pill").forEach((item) => item.classList.remove("selected"));
        button.classList.add("selected");
        selectedSlotId = slot.slotId;
      });
      slotList.appendChild(button);
    });

    selectedSlotId = slots[0].slotId;
  }

  async function refreshSlots() {
    const params = new URLSearchParams({
      storeId: storeSelect.value,
      date: dateInput.value,
      partySize: partySizeSelect.value,
    });
    const { ok, payload } = await requestJson(`/api/slots?${params.toString()}`, { headers: {} });
    if (ok) {
      renderSlots(payload);
    }
  }

  [storeSelect, dateInput, partySizeSelect].forEach((field) => {
    field?.addEventListener("change", () => {
      void refreshSlots();
    });
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (message) message.textContent = "";

    if (!selectedSlotId) {
      if (message) message.textContent = "请先选择一个时段。";
      return;
    }

    const bootstrap = window.NEKOCAFE_BOOTSTRAP || {};
    if (bootstrap.session?.role !== "customer") {
      await loginAs("customer");
    }

    submitButton?.setAttribute("disabled", "disabled");
    const { ok, payload } = await requestJson("/api/reservations", {
      method: "POST",
      body: JSON.stringify({
        storeId: storeSelect.value,
        slotId: selectedSlotId,
        partySize: Number(partySizeSelect.value),
      }),
    });
    submitButton?.removeAttribute("disabled");

    if (!ok) {
      if (message) message.textContent = payload?.detail?.message || "预约失败，请稍后重试。";
      return;
    }

    if (message) message.textContent = "预约成功，正在带你查看会员中心。";
    window.location.href = "/member";
  });
}

bindSessionButtons();
bindStaffActions();
bindBookingForm();
