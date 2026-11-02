# ML systems security curriculum

Study material for low-level machine-learning systems security, aimed at the senior and principal level:
an indexed reading curriculum of about 24,650 hours, a short course, a study guide, worked threat models,
and two small offline study apps.

## Reading curriculum

| File | What it is |
|---|---|
| [ML_Security_Reading_Curriculum_1000h.md](ML_Security_Reading_Curriculum_1000h.md) | Volume I: indexed reading curriculum (~1,740 hours, parts A–K) |
| [ML_Security_Reading_Curriculum_Vol2.md](ML_Security_Reading_Curriculum_Vol2.md) | Volume II: depth and archives (~22,900 hours) |

## Courses and guides

| File | What it is |
|---|---|
| [ML_Systems_Security_Senior_Principal_Guide.md](ML_Systems_Security_Senior_Principal_Guide.md) | Study guide for low-level ML systems security, senior and principal level |
| [ML_Security_8h_Power_Course.md](ML_Security_8h_Power_Course.md) | 8-hour course with answer key |
| [Audit_Tools_README.md](Audit_Tools_README.md) | The audit tool stack and how to use it |

## Study apps (open in any browser, no install)

| File | What it is |
|---|---|
| [ML_Security_Course_App.html](ML_Security_Course_App.html) | Interactive version of the course plus both curriculum volumes as a searchable library; progress export/import |
| [ML_13_Layers_Plan_and_Drills.html](ML_13_Layers_Plan_and_Drills.html) | "ML in 13 layers": a week-by-week plan and timed drills with adaptive weighting toward weak layers |

Both apps keep progress in the browser's `localStorage` and still run (without saving) where storage is blocked.
`_app_source/` holds the build script and Playwright tests for the course app; see its README.

## Threat models and risk assessment

Worked example: a team downloading Hugging Face models and training on a shared GPU cluster.

| File | What it is |
|---|---|
| [Threat_Model_HF_Models_Shared_GPU_Cluster.md](Threat_Model_HF_Models_Shared_GPU_Cluster.md) | Corrected threat model |
| [Threat_Model_HF_Shared_GPU_Gemini_original.md](Threat_Model_HF_Shared_GPU_Gemini_original.md) | The original draft, kept for comparison |
| [Threat_Model_Final.md](Threat_Model_Final.md) | Final version |
| [Threat_Model_Principal_Page2.md](Threat_Model_Principal_Page2.md) | From threat model to directive |
| [Risk_Assessment_Ranking.md](Risk_Assessment_Ranking.md), [Risk_Assessment_Ranking_v1.md](Risk_Assessment_Ranking_v1.md) | Risk ranking (current and first version) |
| [Risk_Scoring_Rubric.md](Risk_Scoring_Rubric.md) | The scoring rubric used |

## Studies

| Folder | What it is |
|---|---|
| [Grid_Containment_Study/](Grid_Containment_Study/) | Pre-registered simulation study: does "electrical grid" containment beat plain baselines for multi-agent security? Pre-registration, simulator, and results |
| [Native Seam Audit/](Native%20Seam%20Audit/) | Procedure for auditing native runtime seams, sanitizer validation with planted-bug controls (`toolcheck/`), and a likelihood × criticality target ranking |
