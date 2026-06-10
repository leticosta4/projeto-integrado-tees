const filterToggle = document.querySelector("[data-filter-toggle]");
const filterPanel = document.getElementById("filter-panel");

function setFilterOpen(isOpen) {
  if (!filterToggle || !filterPanel) {
    return;
  }

  filterToggle.setAttribute("aria-expanded", String(isOpen));
  filterToggle.classList.toggle("active", isOpen);
  filterPanel.toggleAttribute("hidden", !isOpen);
  filterPanel.classList.toggle("open", isOpen);
}

if (filterToggle && filterPanel) {
  filterToggle.addEventListener("click", () => {
    const isOpen = filterToggle.getAttribute("aria-expanded") === "true";
    setFilterOpen(!isOpen);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      setFilterOpen(false);
    }
  });
}
