// Global loader handling for all forms
(function () {
  const loader = document.getElementById("app-loader");
  if (!loader) return;

  function showLoader() {
    loader.classList.remove("d-none");
  }

  // Attach to all forms (application-wide loader)
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      showLoader();
    });
  });
})();

// Patient search + gender filter + status filter
(function () {
  const table = document.getElementById("patients-table");
  if (!table) return;

  const searchInput = document.getElementById("patient-search");
  const filterSelect = document.getElementById("patient-filter");
  const statusFilterSelect = document.getElementById("patient-filter-status");

  function applyFilters() {
    const search = (searchInput?.value || "").toLowerCase().trim();
    const genderFilter = (filterSelect?.value || "").toLowerCase();
    const statusFilter = (statusFilterSelect?.value || "").toLowerCase();

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach((row) => {
      // If the row only has 1 cell (e.g. "No patients found"), ignore it
      if (row.cells.length === 1) return;

      const gender = (row.getAttribute("data-gender") || "").toLowerCase();
      const status = (row.getAttribute("data-status") || "").toLowerCase();

      // Search all text content in the row (searches Name, Phone, Procedure, etc)
      const rowText = (row.textContent || "").toLowerCase();

      const matchesSearch = !search || rowText.includes(search);
      const matchesGender =
        !genderFilter ||
        gender === genderFilter ||
        (genderFilter === "other" &&
          gender !== "male" &&
          gender !== "female" &&
          gender !== "");
          
      const matchesStatus = !statusFilter || status === statusFilter;

      // FIXED: Use direct display manipulation instead of missing CSS classes
      if (matchesSearch && matchesGender && matchesStatus) {
        row.style.display = ""; // Show the row
      } else {
        row.style.display = "none"; // Hide the row
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }
  if (filterSelect) {
    filterSelect.addEventListener("change", applyFilters);
  }
  if (statusFilterSelect) {
    statusFilterSelect.addEventListener("change", applyFilters);
  }
})();

// Theme Toggle (Dark / Light Mode)
(function () {
  const toggleBtn = document.getElementById("theme-toggle");
  if (!toggleBtn) return;

  const iconContainer = document.getElementById("theme-icon-container");
  const themeText = document.getElementById("theme-text");

  // SVG Icons from Bootstrap Icons
  const sunIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-sun-fill" viewBox="0 0 16 16">
      <path d="M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8M8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0m0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13m8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5M3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8m10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0m-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0m9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707M4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708"/>
    </svg>
  `;

  const moonIcon = `
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-moon-stars-fill" viewBox="0 0 16 16">
      <path d="M6 .278a.77.77 0 0 1 .08.858 7.2 7.2 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.306 7.277.868 0 1.71-.15 2.501-.436a.76.76 0 0 1 .798.111c.23.23.292.579.161.862a9 9 0 1 1-9.672-12.28A.77.77 0 0 1 6 .278z"/>
      <path d="M10.794 3.148a.217.217 0 0 1 .412 0l.387 1.162c.173.518.579.924 1.097 1.097l1.162.387a.217.217 0 0 1 0 .412l-1.162.387a1.73 1.73 0 0 0-1.097 1.097l-.387 1.162a.217.217 0 0 1-.412 0l-.387-1.162A1.73 1.73 0 0 0 9.31 6.593l-1.162-.387a.217.217 0 0 1 0-.412l1.162-.387a1.73 1.73 0 0 0 1.097-1.097zM13.863.099a.145.145 0 0 1 .274 0l.258.774c.115.346.386.617.732.732l.774.258a.145.145 0 0 1 0 .274l-.774.258a1.16 1.16 0 0 0-.732.732l-.258.774a.145.145 0 0 1-.274 0l-.258-.774a1.16 1.16 0 0 0-.732-.732l-.774-.258a.145.145 0 0 1 0-.274l.774-.258c.346-.115.617-.386.732-.732z"/>
    </svg>
  `;

  function updateToggleButton(theme) {
    if (theme === "dark") {
      if (iconContainer) iconContainer.innerHTML = sunIcon;
      if (themeText) themeText.textContent = "Light Mode";
      toggleBtn.classList.remove("btn-outline-secondary");
      toggleBtn.classList.add("btn-outline-warning");
    } else {
      if (iconContainer) iconContainer.innerHTML = moonIcon;
      if (themeText) themeText.textContent = "Dark Mode";
      toggleBtn.classList.remove("btn-outline-warning");
      toggleBtn.classList.add("btn-outline-secondary");
    }
  }

  // Get current active theme
  const currentTheme = document.documentElement.getAttribute("data-bs-theme") || "light";
  updateToggleButton(currentTheme);

  // Toggle theme on click
  toggleBtn.addEventListener("click", () => {
    const theme = document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-bs-theme", theme);
    localStorage.setItem("theme", theme);
    updateToggleButton(theme);
  });
})();
