const search = document.querySelector('#stage-query');
if (search) {
  const rows = [...document.querySelectorAll('[data-stage]')];
  const screens = [...document.querySelectorAll('.stage-screen')];
  const count = document.querySelector('#stage-count');
  const empty = document.querySelector('#stage-empty');
  search.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    let visible = 0;
    for (const row of rows) {
      row.hidden = !row.dataset.stage.toLowerCase().includes(query);
      if (!row.hidden) visible += 1;
    }
    for (const screen of screens) {
      screen.hidden = !screen.querySelector('[data-stage]:not([hidden])');
    }
    count.textContent = `${visible} of ${rows.length} destinations`;
    empty.hidden = visible !== 0;
  });
}
