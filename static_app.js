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
