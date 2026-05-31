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

async function loginAs(persona, credentials = {}) {
  return requestJson("/api/session/login", {
    method: "POST",
    body: JSON.stringify({ persona, ...credentials }),
  });
}

async function logoutCurrentSession() {
  return requestJson("/api/session/logout", { method: "POST" });
}

function roleHomePath(role) {
  return {
    customer: "/",
    staff: "/staff",
    admin: "/admin",
  }[role] || "/";
}

function bindSessionButtons() {
  const dialog = document.querySelector("#auth-dialog");
  const authForm = document.querySelector("#auth-form");
  const personaInput = document.querySelector("#auth-persona");
  const identifierInput = document.querySelector("#auth-identifier");
  const secretInput = document.querySelector("#auth-secret");
  const identifierLabel = document.querySelector("#auth-identifier-label");
  const secretLabel = document.querySelector("#auth-secret-label");
  const authHint = document.querySelector("#auth-hint");
  const authMessage = document.querySelector("#auth-message");
  const authSubmit = document.querySelector("#auth-submit");
  const entryOptions = document.querySelectorAll("[data-auth-persona]");

  const authProfiles = {
    customer: {
      identifierLabel: "手机号",
      secretLabel: "会员验证码",
      identifier: "13800001001",
      secret: "260520",
      hint: "演示会员：13800001001 / 260520",
    },
    staff: {
      identifierLabel: "工号 / 账号",
      secretLabel: "门店访问码",
      identifier: "staff-sh-001",
      secret: "SH-NEKO-2026",
      hint: "演示店员：staff-sh-001 / SH-NEKO-2026",
    },
    admin: {
      identifierLabel: "工号 / 账号",
      secretLabel: "管理访问码",
      identifier: "admin-001",
      secret: "ADMIN-NEKO-2026",
      hint: "演示管理员：admin-001 / ADMIN-NEKO-2026",
    },
  };

  function selectPersona(persona) {
    const profile = authProfiles[persona] || authProfiles.customer;
    if (personaInput) personaInput.value = persona;
    if (identifierLabel) identifierLabel.textContent = profile.identifierLabel;
    if (secretLabel) secretLabel.textContent = profile.secretLabel;
    if (identifierInput) identifierInput.value = profile.identifier;
    if (secretInput) secretInput.value = profile.secret;
    if (authHint) authHint.textContent = profile.hint;
    if (authMessage) authMessage.textContent = "";
    entryOptions.forEach((option) => {
      option.classList.toggle("active", option.getAttribute("data-auth-persona") === persona);
    });
  }

  function openAuthDialog(persona = "customer") {
    if (!dialog) return;
    selectPersona(persona);
    dialog.classList.add("open");
    dialog.setAttribute("aria-hidden", "false");
    identifierInput?.focus();
  }

  function closeAuthDialog() {
    if (!dialog) return;
    dialog.classList.remove("open");
    dialog.setAttribute("aria-hidden", "true");
  }

  entryOptions.forEach((button) => {
    button.addEventListener("click", () => {
      selectPersona(button.getAttribute("data-auth-persona") || "customer");
    });
  });

  document.querySelectorAll("[data-auth-close]").forEach((button) => {
    button.addEventListener("click", closeAuthDialog);
  });

  document.querySelectorAll("[data-login-persona]").forEach((button) => {
    button.addEventListener("click", () => {
      const persona = button.getAttribute("data-login-persona");
      if (!persona) return;
      openAuthDialog(persona);
    });
  });

  document.querySelectorAll("[data-login-workspace]").forEach((button) => {
    button.addEventListener("click", () => {
      openAuthDialog("staff");
    });
  });

  authForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const persona = personaInput?.value || "customer";
    const credentials = {
      identifier: identifierInput?.value || "",
    };
    if (persona === "customer") {
      credentials.verificationCode = secretInput?.value || "";
    } else {
      credentials.accessCode = secretInput?.value || "";
    }
    if (authMessage) authMessage.textContent = "";
    authSubmit?.setAttribute("disabled", "disabled");
    const { ok, payload } = await loginAs(persona, credentials);
    authSubmit?.removeAttribute("disabled");
    if (!ok) {
      if (authMessage) authMessage.textContent = payload?.detail?.message || "身份验证失败，请检查输入。";
      return;
    }
    window.location.href = roleHomePath(payload?.role || persona);
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

function bindCustomSelects() {
  const selects = Array.from(document.querySelectorAll("select:not([data-custom-select-bound])"));
  let openSelect = null;

  function closeSelect(instance) {
    if (!instance) return;
    instance.root.classList.remove("open");
    instance.trigger.setAttribute("aria-expanded", "false");
  }

  function closeOpenSelect() {
    closeSelect(openSelect);
    openSelect = null;
  }

  function moveFocus(options, currentIndex, direction) {
    if (!options.length) return;
    const nextIndex = (currentIndex + direction + options.length) % options.length;
    options[nextIndex].focus();
  }

  selects.forEach((select, selectIndex) => {
    select.dataset.customSelectBound = "true";
    select.classList.add("native-select-control");
    select.setAttribute("aria-hidden", "true");
    select.tabIndex = -1;

    const root = document.createElement("div");
    root.className = "custom-select";
    root.dataset.selectName = select.name || select.id || `select-${selectIndex}`;

    const trigger = document.createElement("div");
    trigger.className = "custom-select-trigger";
    trigger.tabIndex = 0;
    trigger.setAttribute("role", "combobox");
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");

    const value = document.createElement("span");
    value.className = "custom-select-value";
    const caret = document.createElement("span");
    caret.className = "custom-select-caret";
    caret.setAttribute("aria-hidden", "true");

    const menu = document.createElement("div");
    menu.className = "custom-select-menu";
    menu.setAttribute("role", "listbox");
    menu.id = `${select.id || select.name || `select-${selectIndex}`}-custom-menu`;
    trigger.setAttribute("aria-controls", menu.id);

    trigger.append(value, caret);
    root.append(trigger, menu);
    select.insertAdjacentElement("afterend", root);

    const instance = { root, trigger, menu };

    function appendOptionItem(option, optionIndex) {
      const item = document.createElement("div");
      item.className = "custom-select-option";
      item.tabIndex = option.disabled ? -1 : 0;
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", option.selected ? "true" : "false");
      item.dataset.value = option.value;
      item.textContent = option.textContent;
      if (option.disabled) item.classList.add("disabled");

      item.addEventListener("click", (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (option.disabled) return;
        select.value = option.value;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        renderOptions();
        closeOpenSelect();
        trigger.focus();
      });

      item.addEventListener("keydown", (event) => {
        const optionNodes = Array.from(menu.querySelectorAll(".custom-select-option:not(.disabled)"));
        const currentIndex = optionNodes.indexOf(item);

        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          item.click();
        }

        if (event.key === "ArrowDown") {
          event.preventDefault();
          moveFocus(optionNodes, currentIndex, 1);
        }

        if (event.key === "ArrowUp") {
          event.preventDefault();
          moveFocus(optionNodes, currentIndex, -1);
        }

        if (event.key === "Escape") {
          event.preventDefault();
          closeOpenSelect();
          trigger.focus();
        }
      });

      if (optionIndex === select.selectedIndex) {
        item.classList.add("selected");
      }
      menu.appendChild(item);
    }

    function renderOptions() {
      const selectedOption = select.selectedOptions[0] || select.options[0];
      value.textContent = selectedOption?.textContent?.trim() || "请选择";
      menu.innerHTML = "";

      let optionIndex = 0;
      Array.from(select.children).forEach((node) => {
        if (node.tagName === "OPTGROUP") {
          const groupLabel = document.createElement("div");
          groupLabel.className = "custom-select-group-label";
          groupLabel.textContent = node.label;
          groupLabel.setAttribute("aria-hidden", "true");
          menu.appendChild(groupLabel);
          Array.from(node.children).forEach((option) => {
            appendOptionItem(option, optionIndex);
            optionIndex += 1;
          });
          return;
        }
        if (node.tagName === "OPTION") {
          appendOptionItem(node, optionIndex);
          optionIndex += 1;
        }
      });
    }

    function openCurrentSelect() {
      if (openSelect && openSelect !== instance) closeSelect(openSelect);
      openSelect = instance;
      root.classList.add("open");
      trigger.setAttribute("aria-expanded", "true");
    }

    trigger.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      if (root.classList.contains("open")) {
        closeOpenSelect();
      } else {
        openCurrentSelect();
      }
    });

    trigger.addEventListener("keydown", (event) => {
      const optionNodes = Array.from(menu.querySelectorAll(".custom-select-option:not(.disabled)"));
      if (event.key === "Enter" || event.key === " " || event.key === "ArrowDown") {
        event.preventDefault();
        openCurrentSelect();
        optionNodes.find((item) => item.classList.contains("selected"))?.focus();
      }
      if (event.key === "Escape") {
        event.preventDefault();
        closeOpenSelect();
      }
    });

    select.addEventListener("change", renderOptions);
    new MutationObserver(renderOptions).observe(select, {
      attributes: true,
      childList: true,
      subtree: true,
    });
    renderOptions();
  });

  document.addEventListener("click", closeOpenSelect);
}

function bindBookingForm() {
  const form = document.querySelector("#booking-form");
  if (!form) return;

  const slotList = document.querySelector("#slot-list");
  const submitButton = document.querySelector("#booking-submit");
  const message = document.querySelector("#booking-message");
  const citySelect = document.querySelector("#city-select");
  const activeCityLabel = document.querySelector("#active-city-label");
  const bookingCityLabel = document.querySelector("#booking-city-label");
  const storeSelect = document.querySelector("#store-select");
  const dateInput = document.querySelector("#date-input");
  const partySizeSelect = document.querySelector("#party-size-select");
  const highlightName = document.querySelector("#store-highlight-name");
  const highlightSummary = document.querySelector("#store-highlight-summary");
  const highlightTags = document.querySelector("#store-highlight-tags");
  const recommendationSummary = document.querySelector("#booking-recommendation-summary");
  const recommendationTags = document.querySelector("#booking-recommendation-tags");
  const recommendationLink = document.querySelector("#booking-recommendation-link");
  const applyRecommendationButton = document.querySelector("[data-apply-recommendation]");
  const summaryStore = document.querySelector("#summary-store");
  const summaryDate = document.querySelector("#summary-date");
  const summaryParty = document.querySelector("#summary-party");
  const summarySlot = document.querySelector("#summary-slot");
  const summaryZone = document.querySelector("#summary-zone");
  const catArchiveLinks = document.querySelectorAll('a[href^="/cats"]');
  const bootstrap = window.NEKOCAFE_BOOTSTRAP || {};
  const recommendationQuery = bootstrap.recommendationQuery || {};
  let selectedSlotId = slotList?.querySelector(".slot-pill.selected")?.getAttribute("data-slot-id") || "";
  const stores = bootstrap.stores || [];
  const storeMap = new Map((bootstrap.stores || []).map((store) => [store.storeId, store]));
  let recommendationMap = new Map((bootstrap.recommendations || []).map((recommendation) => [recommendation.storeId, recommendation]));

  function storesForCity(cityName) {
    return stores.filter((store) => store.cityName === cityName);
  }

  function storeScopeLabel(store) {
    return store ? `${store.cityName}${store.storeName}` : "";
  }

  function activeRecommendation() {
    const cityName = citySelect?.value || "";
    return Array.from(recommendationMap.values()).find((recommendation) => {
      const store = storeMap.get(recommendation.storeId);
      return !cityName || store?.cityName === cityName;
    });
  }

  function renderBookingSummary() {
    const store = storeMap.get(storeSelect?.value);
    const selectedSlot = slotList?.querySelector(".slot-pill.selected");
    const slotTime = selectedSlot?.getAttribute("data-time") || selectedSlot?.querySelector("strong")?.textContent || "";
    const slotZone = selectedSlot?.getAttribute("data-zone") || "";

    if (summaryStore) summaryStore.textContent = store ? `${store.cityName} · ${store.storeName}` : "待选择";
    if (summaryDate) summaryDate.textContent = dateInput?.value || "待选择";
    if (summaryParty) summaryParty.textContent = `${partySizeSelect?.value || bootstrap.defaultPartySize || 2}人`;
    if (summarySlot) summarySlot.textContent = slotTime ? `${slotTime} 到店` : "请选择时段";
    if (summaryZone) summaryZone.textContent = slotZone || "待选择";
  }

  function selectSlotButton(button) {
    if (!slotList || !button) return;
    slotList.querySelectorAll(".slot-pill").forEach((item) => item.classList.remove("selected"));
    button.classList.add("selected");
    selectedSlotId = button.dataset.slotId || "";
    renderBookingSummary();
  }

  function bindSlotButton(button) {
    if (!button || button.dataset.slotBound === "true") return;
    button.dataset.slotBound = "true";
    button.addEventListener("click", () => selectSlotButton(button));
  }

  function renderScopeLabels(storeId) {
    const store = storeMap.get(storeId);
    const label = storeScopeLabel(store);
    if (activeCityLabel && store) activeCityLabel.textContent = store.cityName;
    if (bookingCityLabel && label) bookingCityLabel.textContent = label;
    catArchiveLinks.forEach((link) => {
      if (store) link.setAttribute("href", `/cats?storeId=${store.storeId}`);
    });
  }

  function renderStoreOptions(cityName, preferredStoreId = "") {
    if (!storeSelect) return;
    const cityStores = storesForCity(cityName);
    storeSelect.innerHTML = "";
    cityStores.forEach((store) => {
      const option = document.createElement("option");
      option.value = store.storeId;
      option.textContent = `${store.storeName} · ${store.district}`;
      storeSelect.appendChild(option);
    });
    if (preferredStoreId && cityStores.some((store) => store.storeId === preferredStoreId)) {
      storeSelect.value = preferredStoreId;
    } else if (cityStores.length) {
      storeSelect.value = cityStores[0].storeId;
    }
  }

  function renderStoreHighlight(storeId) {
    const store = storeMap.get(storeId);
    if (!store) return;
    renderScopeLabels(storeId);

    if (highlightName) {
      highlightName.textContent = `${store.storeName} · ${store.district}`;
    }

    if (highlightSummary) {
      highlightSummary.textContent = store.summary;
    }

    if (highlightTags) {
      highlightTags.innerHTML = "";
      store.featureTags.forEach((tag) => {
        const node = document.createElement("span");
        node.textContent = tag;
        highlightTags.appendChild(node);
      });
    }

    const recommendation = recommendationMap.get(storeId);
    if (recommendationSummary && recommendationTags && recommendationLink) {
      const tags = recommendation?.reasonTags || store.featureTags;
      recommendationSummary.textContent = recommendation?.detail || store.summary;
      recommendationTags.innerHTML = "";
      tags.forEach((tag) => {
        const node = document.createElement("span");
        node.textContent = tag;
        recommendationTags.appendChild(node);
      });
      const activeDate = dateInput?.value || recommendationQuery.date || bootstrap.defaultDate;
      const activePartySize = partySizeSelect?.value || recommendationQuery.partySize || bootstrap.defaultPartySize;
      recommendationLink.setAttribute("href", `/?storeId=${store.storeId}&date=${activeDate}&partySize=${activePartySize}`);
    }
    renderBookingSummary();
  }

  function renderSlots(slots) {
    if (!slotList) return;
    slotList.innerHTML = "";

    if (!slots.length) {
      slotList.innerHTML = '<p class="metric-note">暂时没有符合条件的时段，可以调整人数、日期或换一家门店。</p>';
      selectedSlotId = "";
      renderBookingSummary();
      return;
    }

    slots.forEach((slot, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `slot-pill ${index === 0 ? "selected" : ""}`;
      button.dataset.slotId = slot.slotId;
      button.dataset.time = slot.startAt.slice(11, 16);
      button.dataset.zone = slot.zoneName;
      button.innerHTML = `<strong>${slot.startAt.slice(11, 16)}</strong><span>${slot.zoneName} · 余${slot.remainingCapacity}位</span>`;
      bindSlotButton(button);
      slotList.appendChild(button);
    });

    selectedSlotId = slots[0].slotId;
    renderBookingSummary();
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

  async function refreshRecommendations() {
    if (!storeSelect || !dateInput || !partySizeSelect) return;
    const params = new URLSearchParams({
      date: dateInput.value,
      partySize: partySizeSelect.value,
      city: citySelect?.value || "",
    });
    const { ok, payload } = await requestJson(`/api/recommendations/me?${params.toString()}`, { headers: {} });
    if (ok && Array.isArray(payload)) {
      recommendationMap = new Map(payload.map((recommendation) => [recommendation.storeId, recommendation]));
    }
    renderStoreHighlight(storeSelect.value);
  }

  citySelect?.addEventListener("change", () => {
    renderStoreOptions(citySelect.value);
    renderStoreHighlight(storeSelect.value);
    void refreshSlots();
    void refreshRecommendations();
  });

  [storeSelect, dateInput, partySizeSelect].forEach((field) => {
    field?.addEventListener("change", () => {
      if (field === storeSelect) renderStoreHighlight(storeSelect.value);
      renderBookingSummary();
      void refreshSlots();
      void refreshRecommendations();
    });
  });

  applyRecommendationButton?.addEventListener("click", () => {
    const recommendation = activeRecommendation();
    const store = recommendation ? storeMap.get(recommendation.storeId) : null;
    if (!store || !citySelect || !storeSelect) return;
    citySelect.value = store.cityName;
    renderStoreOptions(store.cityName, store.storeId);
    renderStoreHighlight(store.storeId);
    void refreshSlots();
    void refreshRecommendations();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (message) message.textContent = "";

    if (!selectedSlotId) {
      if (message) message.textContent = "请选择一个可预约时段后再提交。";
      return;
    }

    if (bootstrap.session?.role !== "customer") {
      if (message) message.textContent = "请先通过会员入口完成身份验证后再预约。";
      document.querySelector('[data-login-persona="customer"]')?.click();
      return;
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

    if (message) message.textContent = "预约已确认，正在打开预约详情。";
    window.location.href = `/reservations/${payload.reservationId}`;
  });

  if (citySelect) {
    renderStoreOptions(citySelect.value, storeSelect.value);
  }
  slotList?.querySelectorAll(".slot-pill").forEach(bindSlotButton);
  renderStoreHighlight(storeSelect.value);
  renderBookingSummary();
}

bindSessionButtons();
bindStaffActions();
bindBookingForm();
bindCustomSelects();
