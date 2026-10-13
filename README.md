# AI Conveyor Belt Smart Packing Suggestion

## Product Requirements and Engineering Roadmap

**Project type:** Fifth-semester academic engineering prototype\
**Owner:** Likith Reddy\
**Repository name:** `ai-conveyor-belt-quality-monitoring`\
**Status:** Existing prototype under review; requirements below are a
target specification, not a claim that every feature is implemented or
validated.

------------------------------------------------------------------------

## 1. Product Vision

Develop a portfolio-quality prototype that uses computer vision and
camera/depth measurements to inspect objects moving on a conveyor,
estimate their dimensions, recommend a suitable packaging box, and
present results in a clear operator-facing interface.

The repository must distinguish between: - **Implemented:** evidenced by
source code and reproducible tests. - **In progress:** partially
implemented and requiring validation. - **Planned:** a target for future
development.

Do not describe planned features as completed functionality.

## 2. Goals

1.  Measure object dimensions in a repeatable, documented way.
2.  Recommend a packaging option from a configurable catalogue.
3.  Provide understandable measurement/recommendation output.
4.  Make setup and limitations clear to another engineer.
5.  Keep the code reproducible, testable, secure, and suitable for a
    public GitHub portfolio.

## 3. Scope

### In scope

-   Camera input and image processing.
-   Camera/measurement calibration.
-   Object dimension estimation.
-   Packaging catalogue and recommendation logic.
-   Error handling for missing configuration or camera access.
-   Clear setup instructions and sample outputs.
-   Unit tests for packaging logic and configuration validation.
-   Documentation of hardware and measurement accuracy.

### Out of scope unless separately implemented

-   Production-grade industrial safety certification.
-   Guaranteed measurement accuracy without controlled testing.
-   Live PLC/industrial controller integration.
-   Production deployment, cloud telemetry, authentication, or
    multi-user management.
-   Claims of AI/YOLO inference unless a trained model and inference
    path are actually present and tested.

## 4. Functional Requirements

  ----------------------------------------------------------------------------------
  ID                Requirement              Acceptance criteria   Priority
  ----------------- ------------------------ --------------------- -----------------
  FR-01             Camera initialization    App checks camera     Must
                                             availability and      
                                             reports a useful      
                                             error if unavailable. 

  FR-02             Object                   System identifies a   Must
                    detection/segmentation   target object in a    
                                             frame under           
                                             documented            
                                             lighting/background   
                                             conditions.           

  FR-03             Dimension estimation     System returns length Must
                                             and width, and height 
                                             when supported by the 
                                             chosen camera         
                                             workflow, with units  
                                             stated explicitly.    

  FR-04             Calibration              Calibration workflow  Must
                                             saves validated       
                                             values to a           
                                             documented            
                                             configuration file;   
                                             invalid or missing    
                                             values are rejected.  

  FR-05             Packaging catalogue      Box options are       Must
                                             stored in a           
                                             documented CSV/JSON   
                                             schema with unique    
                                             IDs and positive      
                                             dimensions.           

  FR-06             Box recommendation       Algorithm selects a   Must
                                             box that fits the     
                                             object with a         
                                             configurable          
                                             clearance margin, or  
                                             reports that no box   
                                             fits.                 

  FR-07             Operator output          Display/log object    Should
                                             dimensions, selected  
                                             box, and a reason for 
                                             the recommendation.   

  FR-08             Failure handling         Missing camera,       Must
                                             calibration,          
                                             catalogue, or         
                                             malformed inputs      
                                             produce actionable    
                                             messages instead of   
                                             an unexplained crash. 

  FR-09             Measurement record       Optional CSV logging  Should
                                             records timestamp,    
                                             dimensions, units,    
                                             and recommendation    
                                             without storing       
                                             unnecessary personal  
                                             data.                 

  FR-10             Web interface            If a Flask UI is      Should
                                             retained, it must be  
                                             clearly labelled as a 
                                             prototype until the   
                                             measurement pipeline  
                                             is connected and      
                                             verified.             

  FR-11             Model training           Training only runs    Should
                                             when a valid dataset  
                                             config, labels,       
                                             images, and           
                                             dependencies are      
                                             supplied. Training    
                                             and inference status  
                                             must be documented    
                                             separately.           

  FR-12             Tests                    Automated tests cover Must
                                             catalogue validation, 
                                             fit/clearance logic,  
                                             and invalid inputs.   
  ----------------------------------------------------------------------------------

## 5. Non-functional Requirements

-   **Reproducibility:** document supported Python version and
    dependency installation.
-   **Maintainability:** use clear module/file names, functions,
    comments for non-obvious calculations, and consistent units.
-   **Reliability:** validate inputs and handle common
    hardware/configuration failures.
-   **Safety:** do not directly control conveyor motors or actuators
    without an independently reviewed safety design and emergency-stop
    strategy.
-   **Performance:** record actual frame rate/processing latency during
    testing; do not invent benchmark figures.
-   **Privacy:** do not commit private images, personal information,
    credentials, or environment files.
-   **Portability:** explain hardware-specific requirements, especially
    depth-camera SDK support.
-   **Accessibility/usability:** make errors and measurements legible
    and use explicit units.

## 6. Measurement and Calibration Requirements

1.  State the camera model and mounting arrangement used in the actual
    setup.
2.  Document calibration target, procedure, saved fields, and expected
    units.
3.  Never fabricate calibration constants to make the application run.
4.  Reject empty, non-numeric, zero, negative, or out-of-range
    calibration values.
5.  Validate measurements against objects with known dimensions.
6.  Record absolute error and percentage error for each test object.
7.  Repeat measurements under more than one position/lighting condition.
8.  Clearly state that accuracy is unverified until these tests have
    been performed.

Suggested validation table:

  --------------------------------------------------------------------------
  Test object Reference L × Measured L  Absolute    Conditions   Pass/Fail
              W × H         × W × H     error                    
  ----------- ------------- ----------- ----------- ------------ -----------
  Sample A    Fill after    Fill after  Calculate   Record       Pending
              measurement   test                                 

  Sample B    Fill after    Fill after  Calculate   Record       Pending
              measurement   test                                 

  Sample C    Fill after    Fill after  Calculate   Record       Pending
              measurement   test                                 
  --------------------------------------------------------------------------

Do not fill this table with invented results.

## 7. Packaging Recommendation Rules

-   Use one documented unit system throughout the calculation
    (preferably millimetres).
-   Validate that all object and box dimensions are positive numbers.
-   Support a configurable clearance margin.
-   Define whether object rotation is allowed and which orientations are
    evaluated.
-   Recommend only boxes that fit the object under the documented rules.
-   If no box fits, return a clear "no suitable box found" result.
-   Include the selected box ID and internal dimensions in the output.
-   Test exact-fit, clearance, rotated-fit, invalid dimensions, and
    no-fit cases.

## 8. Repository and Documentation Requirements

The GitHub repository should contain: - `README.md` --- overview,
features, hardware, setup, usage, limitations, screenshots, tests, and
roadmap. - `PROJECT_REQUIREMENTS.md` --- this specification. -
`requirements.txt` --- verified Python dependencies, ideally pinned to
tested versions. - `.gitignore` --- Python cache, virtual environments,
local secrets, generated measurements, datasets, and model artifacts. -
`tests/` --- automated tests for deterministic logic. - `docs/` ---
wiring diagram, system architecture, calibration procedure, and test
report when available. - `LICENSE` --- choose a license only after
confirming that you have the right to publish all included
code/assets. - `assets/` --- only non-sensitive, project-owned
screenshots/diagrams that are useful for explaining the system.

Do not commit `.venv/`, passwords, tokens, `.env`, private data,
unnecessary macOS metadata, or large datasets/model weights without a
deliberate reason.

## 9. Existing Archive Review --- Known Issues to Resolve

Based on the supplied ZIP archive: - `depth_calib.json` exists but is
empty. - The code refers to supporting files such as `box_catalog.csv`
and `data.yaml`, but these were not present in the archive. - Model
weights and a complete training dataset were not present in the
archive. - `app.py` appears to be a minimal Flask placeholder and must
not be presented as a completed dashboard unless it is developed and
tested. - `measure_and_recommend.py` and
`measure_and_recommend_depth.py` appear to contain very similar
workflows; identify the canonical entry point or document why both are
retained. - A file named `import pandas as pd.py` appears to be an
accidental scratch file; inspect it and remove it if it is not a genuine
module. - Basic syntax parsing is not the same as hardware or end-to-end
validation.

These findings are based on the archive contents and should be rechecked
after extraction.

## 10. Recommended Implementation Order

1.  Preserve the original project and create a separate Git branch or
    backup.
2.  Remove accidental files and macOS metadata after reviewing them.
3.  Add `README.md`, this requirements file, `.gitignore`, and a
    dependency file.
4.  Define and validate the packaging catalogue schema.
5.  Make calibration loading fail safely when values are absent or
    invalid.
6.  Add unit tests for packaging recommendation logic.
7.  Test the camera pipeline on the actual supported hardware.
8.  Record real measurement accuracy results and sample screenshots.
9.  Verify a clean installation in a new virtual environment.
10. Review Git status for secrets, generated files, and large artifacts.
11. Commit and push to GitHub.
12. Add a concise architecture diagram and demonstration video only when
    genuine project assets are available.

## 11. Definition of Done for a Portfolio Release

A release is ready to share when: - A new user can follow the README
without guessing missing steps. - Dependencies and hardware requirements
are explicit. - Required configuration/catalogue files are supplied or
generated by documented steps. - Automated tests pass for deterministic
business logic. - Hardware-specific limitations are stated honestly. -
At least one end-to-end test is recorded, if hardware is available. -
Measurement accuracy is reported only from real tests. - The repository
contains no secrets or accidental files. - All screenshots, diagrams,
and datasets are owned or appropriately licensed. - The GitHub
description and README accurately represent the implementation status.

## 12. GitHub Repository Metadata

**Suggested repository name:** `ai-conveyor-belt-quality-monitoring`

**Suggested description:**\
`Computer-vision conveyor inspection prototype for object dimension estimation and packaging recommendation using Python and OpenCV, with camera calibration and depth-camera experimentation.`

**Suggested topics:**\
`computer-vision`, `opencv`, `python`, `robotics`,
`industrial-automation`, `conveyor-belt`, `object-measurement`,
`packaging-optimization`

Use only topics and claims that match the final code. Update this
document as requirements are implemented and verified.
