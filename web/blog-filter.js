const filterButtons = [...document.querySelectorAll(".blog-filters [data-filter]")];
const articleCards = [...document.querySelectorAll(".blog-card[data-category]")];
const filterStatus = document.querySelector(".blog-filter-status");
const emptyState = document.querySelector(".blog-empty-state");

if (filterButtons.length && articleCards.length && filterStatus && emptyState) {
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedFilter = button.dataset.filter;
      let visibleCount = 0;

      filterButtons.forEach((filterButton) => {
        filterButton.setAttribute("aria-pressed", String(filterButton === button));
      });

      articleCards.forEach((card) => {
        const isVisible = selectedFilter === "all" || card.dataset.category === selectedFilter;
        card.hidden = !isVisible;
        visibleCount += Number(isVisible);
      });

      filterStatus.textContent = `Showing ${visibleCount} ${visibleCount === 1 ? "article" : "articles"}`;
      emptyState.hidden = visibleCount > 0;
    });
  });
}
