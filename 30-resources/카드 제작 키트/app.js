(function () {
  "use strict";

  const STORAGE_KEY = "career-lens-doers-ax-card-v1";
  const originalData = structuredClone(window.JOB_CARD_DATA);
  let cardData = loadStoredData() || structuredClone(originalData);
  let editMode = false;

  const card = document.getElementById("job-card");
  const stage = document.getElementById("card-stage");
  const editToggle = document.getElementById("edit-toggle");
  const jsonToggle = document.getElementById("json-toggle");
  const jsonPanel = document.getElementById("json-panel");
  const jsonEditor = document.getElementById("json-editor");
  const jsonError = document.getElementById("json-error");
  const saveStatus = document.getElementById("save-status");

  function loadStoredData() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : null;
    } catch (error) {
      console.warn("저장된 카드 데이터를 불러오지 못했습니다.", error);
      return null;
    }
  }

  function getValue(path) {
    return path.split(".").reduce((value, key) => value?.[key], cardData);
  }

  function setValue(path, nextValue) {
    const keys = path.split(".");
    const lastKey = keys.pop();
    const target = keys.reduce((value, key) => value[key], cardData);
    target[lastKey] = nextValue;
  }

  function renderTerm(element, text) {
    const separator = text.indexOf(":");
    if (separator < 0) {
      element.textContent = text;
      return;
    }

    const label = document.createElement("strong");
    label.textContent = text.slice(0, separator + 1);
    element.replaceChildren(label, document.createTextNode(text.slice(separator + 1)));
  }

  function renderCompetency(element, text) {
    const marker = "[우대]";
    if (!text.startsWith(marker)) {
      element.textContent = text;
      return;
    }

    const label = document.createElement("strong");
    label.textContent = marker;
    element.replaceChildren(label, document.createTextNode(text.slice(marker.length)));
  }

  function render() {
    document.querySelectorAll("[data-bind]").forEach((element) => {
      const value = getValue(element.dataset.bind);
      const text = value ?? "";
      if (element.matches(".info-list--terms li")) {
        renderTerm(element, text);
      } else if (element.matches(".info-list--competencies li")) {
        renderCompetency(element, text);
      } else {
        element.textContent = text;
      }
    });
    jsonEditor.value = JSON.stringify(cardData, null, 2);
  }

  function persist(message) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cardData));
    saveStatus.textContent = message;
    window.clearTimeout(persist.timer);
    persist.timer = window.setTimeout(() => {
      saveStatus.textContent = "자동 저장됨";
    }, 1200);
  }

  function setEditMode(nextMode) {
    editMode = nextMode;
    card.classList.toggle("editing", editMode);
    editToggle.setAttribute("aria-pressed", String(editMode));
    editToggle.textContent = editMode ? "편집 완료" : "직접 편집";

    document.querySelectorAll(".editable").forEach((element) => {
      element.contentEditable = String(editMode);
      element.spellcheck = false;
    });

    saveStatus.textContent = editMode
      ? "점선 안의 문구를 클릭해 수정하세요"
      : "자동 저장됨";
  }

  function updateScale() {
    const scale = stage.clientWidth / 794;
    card.style.setProperty("--card-scale", String(scale));
  }

  editToggle.addEventListener("click", () => setEditMode(!editMode));

  document.querySelectorAll(".editable").forEach((element) => {
    element.addEventListener("input", () => {
      const nextValue = element.textContent.trim();
      setValue(element.dataset.bind, nextValue || (element.dataset.bind === "circleTitle.2" ? "\u00a0" : ""));
      persist("문구 저장 중");
    });

    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        element.blur();
      }
    });

    element.addEventListener("paste", (event) => {
      event.preventDefault();
      const text = event.clipboardData.getData("text/plain").replace(/\s*\n\s*/g, " ");
      document.execCommand("insertText", false, text);
    });
  });

  jsonToggle.addEventListener("click", () => {
    const willOpen = jsonPanel.hidden;
    jsonPanel.hidden = !willOpen;
    jsonToggle.setAttribute("aria-expanded", String(willOpen));
    if (willOpen) {
      jsonEditor.value = JSON.stringify(cardData, null, 2);
      jsonEditor.focus();
    }
  });

  document.getElementById("apply-json").addEventListener("click", () => {
    try {
      cardData = JSON.parse(jsonEditor.value);
      render();
      persist("JSON 적용 완료");
      jsonError.textContent = "";
    } catch (error) {
      jsonError.textContent = `JSON 확인 필요: ${error.message}`;
    }
  });

  document.getElementById("download-json").addEventListener("click", () => {
    const blob = new Blob([JSON.stringify(cardData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "career-lens-doers-ax-card.json";
    link.click();
    URL.revokeObjectURL(url);
    saveStatus.textContent = "JSON 파일 저장 완료";
  });

  document.getElementById("reset-card").addEventListener("click", () => {
    if (!window.confirm("모든 문구를 초기 상태로 되돌릴까요?")) return;
    cardData = structuredClone(originalData);
    localStorage.removeItem(STORAGE_KEY);
    render();
    saveStatus.textContent = "초기화 완료";
  });

  document.getElementById("print-card").addEventListener("click", () => {
    setEditMode(false);
    window.print();
  });

  new ResizeObserver(updateScale).observe(stage);
  window.addEventListener("beforeprint", () => card.style.setProperty("--card-scale", "1"));
  window.addEventListener("afterprint", updateScale);

  render();
  updateScale();
})();
