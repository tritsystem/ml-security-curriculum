ML Security course app: how to update it without Claude

The app is ML_Security_Course_App.html (one folder up). Just open it in any browser; nothing else is needed.

To change the content:
1. Edit the source text: ML_Security_8h_Power_Course.md (course and answer key) or the two curriculum volumes
   (library tables).
2. Rebuild:   python build_app.py          (needs: pip install markdown)
3. Optional test:  python test_app.py      (needs: pip install playwright && playwright install chromium)

Your progress lives in the browser (localStorage). Before rebuilding or switching devices, use
Progress & backup -> Export progress, then Import on the other side. Rebuilding does not erase progress
as long as you open the file in the same browser.
