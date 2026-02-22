# Dashboard Change Log (vs original `natsawin.py`)

## Compared files
- Original: `Tle/natsawin.py`
- Current: `Moss/Test_Latest_Streamlit.py`

## Summary
This dashboard was upgraded from a basic Streamlit prototype into a more polished and interactive analytics app with improved UI theme, filter UX, chart readability, map behavior, and table usability.

## What changed

### 1) Theme / Visual style
- Changed global color theme from bright cyan to a softer indigo/slate style.
- Updated app background, sidebar background, metric card styling, shadow, and heading color.
- Improved contrast and readability across charts and cards.

### 2) Sidebar filters and reset UX
- Added stable widget keys for all sidebar controls.
- Added **Reset Filters** button that resets all input widgets to defaults (not only data output).
- Added **Top skills in treemap** slider (`5–25`, default `12`).

### 3) Header improvements
- Changed title text to include role scope:
  - `Job Market Dashboard (Data Science & Data Engineer & Data Analyst)`
- Added automatic **Latest update timestamp** in header by scanning CSV filenames inside `Moss/Scraped_All` and extracting newest date/time.

### 4) Row-1 charts (Salary / Web / Avg Salary)
- Set fixed chart heights for visual alignment.
- Salary and Avg Salary bars updated to new color palette.
- Replaced old Matplotlib pie in **Job Per Web** with Plotly hierarchical chart (sunburst):
  - Inner level: Website
  - Outer level: Keyword ratio
- Hid Plotly modebar for cleaner UI in this section.

### 5) Province map (Job Per Province)
- Improved map styling and readability:
  - Better projection and centering
  - Stronger province border lines
  - Updated color scale and map colors
- Made map background transparent.
- Disabled zoom interactions / scroll zoom.
- Removed map legend (color bar) for cleaner display.
- Adjusted chart sizing/layout balance with treemap.

### 6) Skill treemap (Job Skill)
- Unified color palette with dashboard theme.
- Added top-N control via sidebar slider.
- Removed `Other` aggregation logic for skill treemap (now shows top N actual skills only).
- Hid Plotly modebar in this section.

### 7) Job table
- Replaced custom HTML table with native `st.dataframe` (scrollable table).
- Added clickable link column using `st.column_config.LinkColumn`.
- Sorted rows by **Posted Date** descending (latest first).
- Formatted date as `YYYY-MM-DD`.
- Added **Download filtered data (CSV)** button.

### 8) Empty-state handling
- Added user messages when filtered results are empty, including:
  - No jobs for current filters
  - No salary data
  - No position salary data
  - No skill data / no rows

## Behavior differences from original
- More interactive and consistent chart experience (Plotly-first approach).
- Cleaner layout and reduced visual clutter (hidden modebars, better spacing/alignment).
- Filter reset is now reliable for both data and widget state.
- Table is now practical for large data (scroll + sort + download).

## Notes
- `Job Per Web` still groups low-frequency keywords into `Other` (only in sunburst web-keyword chart).
- Skill treemap no longer uses `Other` bucket.
