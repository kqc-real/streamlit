# MC-Test Mermaid Diagrams

This file collects Mermaid diagrams that describe MC-Test from product,
runtime, data, export, and governance perspectives. Mermaid diagrams are the
single source of truth for repository diagrams.

## 1) System Overview

```mermaid
flowchart LR
    student["Learner"]
    instructor["Instructor or content author"]
    admin["Admin"]
    llm["External LLM"]

    subgraph app["MC-Test Streamlit app"]
        home["Start page and legal pages"]
        pseudonym["Pseudonym workflow"]
        setselect["Question-set selection"]
        testview["Question view"]
        summary["Evaluation and review"]
        adminpanel["Admin panel"]
    end

    subgraph content["Question content"]
        bundled["Bundled sets in data/"]
        uploads["Temporary uploaded sets in data-user/"]
        objectives["Learning objectives"]
        prompts["External LLM prompts"]
    end

    subgraph persistence["SQLite persistence"]
        users["Users and pseudonyms"]
        sessions["Sessions"]
        answers["Answers"]
        feedback["Feedback and bookmarks"]
        summaries["Session summaries"]
        audit["Admin audit log"]
    end

    subgraph outputs["Outputs"]
        pdf["PDF"]
        csv["CSV and analysis"]
        anki["Anki APKG or TSV"]
        arsnova["arsnova.eu JSON"]
    end

    student --> home --> pseudonym --> setselect --> testview --> summary --> outputs
    instructor --> prompts --> llm --> bundled
    instructor --> uploads --> setselect
    admin --> adminpanel --> persistence
    testview --> answers
    testview --> feedback
    pseudonym --> users
    testview --> sessions
    summary --> summaries
    bundled --> setselect
    objectives --> summary
```

## 2) Learner Journey

```mermaid
flowchart TD
    start(["Open MC-Test"])
    legal["Legal notice and privacy policy are reachable"]
    choosePath{"Choose path"}
    ready["Use a bundled question set"]
    upload["Upload or create a set with an external LLM"]
    pseudonym["Choose pseudonym"]
    secret{"Reserve pseudonym?"}
    noSecret["Session-only pseudonym"]
    withSecret["Set and confirm recovery secret"]
    set["Select question set, sort order, pace, and mode"]
    mode{"Mode"}
    exam["Exam mode: timer, pacer, leaderboard summary"]
    practice["Practice mode: immediate feedback and explanation"]
    question["Answer, skip, bookmark, or review a question"]
    done{"All questions done or session ended?"}
    summary["Review score, concepts, cognitive stages, and explanations"]
    export{"Export needed?"}
    exportFiles["Generate PDF, CSV, Anki, or arsnova.eu JSON"]
    finish(["Learning evidence is available"])

    start --> legal --> choosePath
    choosePath --> ready --> pseudonym
    choosePath --> upload --> pseudonym
    pseudonym --> secret
    secret --> noSecret --> set
    secret --> withSecret --> set
    set --> mode
    mode --> exam --> question
    mode --> practice --> question
    question --> done
    done -- no --> question
    done -- yes --> summary
    summary --> export
    export -- yes --> exportFiles --> finish
    export -- no --> finish
```

## 3) Test Session State Model

```mermaid
stateDiagram-v2
    [*] --> Splash
    Splash --> PseudonymSelection: choose question-set path
    Splash --> LLMWorkflow: choose external LLM path
    LLMWorkflow --> Splash: close workflow
    LLMWorkflow --> PseudonymSelection: set is ready

    PseudonymSelection --> SetSelection: valid pseudonym
    PseudonymSelection --> ReservedLogin: existing reserved pseudonym
    ReservedLogin --> SetSelection: secret verified

    SetSelection --> ActiveExam: start exam mode
    SetSelection --> ActivePractice: start practice mode

    ActiveExam --> ActiveExam: answer, skip, bookmark, next
    ActivePractice --> ActivePractice: answer, feedback, explanation, next
    ActiveExam --> FinalSummary: completed, expired, or ended
    ActivePractice --> FinalSummary: completed or ended

    FinalSummary --> ExportReview: export or review records
    FinalSummary --> SetSelection: start another set
    FinalSummary --> Splash: reset to start page
    ExportReview --> FinalSummary: return
    FinalSummary --> [*]
```

## 4) Answer Submission and Persistence

```mermaid
sequenceDiagram
    actor Learner
    participant UI as Streamlit question view
    participant State as st.session_state
    participant Logic as logic.py
    participant DB as SQLite via database.py
    participant Summary as summary/review

    Learner->>UI: Select answer
    UI->>State: Store selected option widget state
    Learner->>UI: Submit answer
    UI->>Logic: Check correct answer and score
    Logic-->>UI: points, correctness, feedback state
    UI->>DB: save_answer with retry and write transaction
    DB-->>UI: answer persisted
    UI->>State: Mark question answered

    alt Practice mode
        UI-->>Learner: Show immediate feedback and explanation
        UI-->>Learner: Scroll toward Next button area
    else Exam mode
        UI-->>Learner: Keep feedback hidden until summary
    end

    UI->>Summary: Recompute progress indicators
    Summary-->>Learner: Timer, pacer, score, and remaining questions update
```

## 5) Data Model

This diagram intentionally uses a styled flowchart instead of Mermaid `erDiagram`
tables. Some renderers apply alternating ER row backgrounds that can become
unreadable in dark mode.

```mermaid
flowchart TB
    users["users<br/>PK user_id : text<br/>user_pseudonym : text<br/>recovery_salt : text<br/>recovery_hash : text"]
    sessions["test_sessions<br/>PK session_id : integer<br/>FK user_id : text<br/>questions_file : text<br/>start_time : timestamp<br/>tempo : text<br/>mode : text"]
    answers["answers<br/>PK answer_id : integer<br/>FK session_id : integer<br/>question_nr : integer<br/>answer_text : text<br/>points : integer<br/>is_correct : boolean<br/>confidence : text<br/>timestamp : timestamp"]
    bookmarks["bookmarks<br/>PK bookmark_id : integer<br/>FK session_id : integer<br/>question_nr : integer"]
    feedback["feedback<br/>PK feedback_id : integer<br/>FK session_id : integer<br/>question_nr : integer<br/>feedback_type : text<br/>timestamp : timestamp"]
    summaries["test_session_summaries<br/>PK session_id : integer<br/>user_id : text<br/>user_pseudonym : text<br/>questions_file : text<br/>questions_title : text<br/>question_count : integer<br/>total_points : integer<br/>max_points : integer<br/>correct_count : integer<br/>percent : real<br/>time_expired : boolean<br/>exported : boolean"]
    prefs["user_preferences<br/>PK user_pseudonym : text<br/>PK pref_key : text<br/>pref_value : text"]
    audit["admin_audit_log<br/>PK id : integer<br/>timestamp : text<br/>user_id : text<br/>action : text<br/>details : text<br/>success : boolean"]

    users -->|starts 0..n| sessions
    sessions -->|stores 0..n| answers
    sessions -->|marks 0..n| bookmarks
    sessions -->|receives 0..n| feedback
    sessions -->|summarizes 0..1| summaries
    users -->|has 0..n| prefs
    users -->|may create 0..n| audit

    classDef table fill:#1f2937,stroke:#94a3b8,stroke-width:1px,color:#e5e7eb;
    classDef core fill:#172033,stroke:#60a5fa,stroke-width:1px,color:#e5e7eb;
    class users,sessions,summaries core;
    class answers,bookmarks,feedback,prefs,audit table;
```

## 6) Export Pipeline

```mermaid
flowchart LR
    summary["Final summary or review mode"]
    choose{"Choose export format"}
    gather["Load questions, answers, metadata, explanations, glossary"]
    normalize["Normalize Markdown, safe HTML, LaTeX, and answer order"]

    pdf["PDF renderer"]
    csv["CSV or analysis table"]
    anki["Anki APKG or TSV generator"]
    arsnova["arsnova.eu JSON mapper"]

    download["Download file"]

    summary --> choose --> gather --> normalize
    normalize --> pdf --> download
    normalize --> csv --> download
    normalize --> anki --> download
    normalize --> arsnova --> download

    anki -. guard .-> noNested["Avoid nested ABCD numbering"]
    arsnova -. guard .-> readable["Keep content readable if advanced Markdown is flattened"]
    pdf -. guard .-> visual["Visually check rendering after Markdown or CSS changes"]
```

## 7) External LLM Content Workflow

```mermaid
flowchart TD
    author["Content author"]
    appPrompt["App provides raw external LLM prompt"]
    externalLLM["External LLM"]
    rawJSON["Canonical question-set JSON"]
    validate["Validate with validate_sets.py"]
    save["Save as data/questions_<Set>.json"]
    learningPrompt["Micro learning-objectives prompt"]
    objectives["data/questions_<Set>_Learning_Objectives.md"]
    qaQuestion["Question-set QA postproduction"]
    qaObjectives["Learning-objectives QA postproduction"]
    finalSet["Validated learning-ready set"]

    author --> appPrompt --> externalLLM --> rawJSON
    rawJSON --> validate
    validate -- errors --> rawJSON
    validate -- valid --> save
    save --> learningPrompt --> objectives
    save --> qaQuestion --> finalSet
    objectives --> qaObjectives --> finalSet

    appPrompt -. rule .-> selfContained["Prompt is US English and self-contained"]
    rawJSON -. rule .-> canonical["English JSON keys, content language from meta.language"]
    finalSet -. rule .-> noRemovedTargets["No Kahoot or arsnova.click targets"]
```

## 8) Privacy and Legal Boundary

```mermaid
flowchart TB
    public["Public Streamlit deployment"]
    legal["Legal Notice / Impressum"]
    privacy["Privacy Policy / Datenschutzerklaerung"]
    runtime["Streamlit runtime"]
    app["MC-Test app logic"]
    sqlite["SQLite database"]
    uploads["Question-set uploads"]
    exports["User-triggered exports"]

    subgraph stored["Stored by app"]
        pseudonym["Pseudonym"]
        sessionStats["Session, answer, feedback, bookmark, and summary data"]
        secretHash["Reserved pseudonym recovery secret hash"]
        audit["Admin audit and login attempts"]
    end

    subgraph notOwned["Not app-owned tracking"]
        noAds["No ads"]
        noMarketing["No marketing tracking cookies"]
        noAnalytics["No app-owned analytics tracking"]
    end

    public --> legal
    public --> privacy
    public --> runtime --> app
    app --> sqlite
    sqlite --> pseudonym
    sqlite --> sessionStats
    sqlite --> secretHash
    sqlite --> audit
    app --> uploads
    app --> exports
    runtime -. may use .-> technicalStorage["Technically necessary runtime cookies or browser storage"]
    app -. must not claim .-> noAds
    app -. must not claim .-> noMarketing
    app -. must not claim .-> noAnalytics
```

## 9) SQLite Write Path Under Load

```mermaid
sequenceDiagram
    participant UI1 as User session A
    participant UI2 as User session B
    participant Retry as with_db_retry
    participant Lock as process-wide write lock
    participant DB as SQLite WAL database

    UI1->>Retry: start_test_session or save_answer
    Retry->>Lock: enter db_write_transaction
    Lock->>DB: write transaction
    DB-->>Lock: commit
    Lock-->>Retry: release
    Retry-->>UI1: success

    UI2->>Retry: concurrent write
    Retry->>Lock: wait for serialized writer
    Lock->>DB: write transaction
    alt lock or busy error
        DB-->>Retry: lock/busy
        Retry->>Retry: backoff
        Retry->>Lock: retry transaction
    else success
        DB-->>Lock: commit
    end
    Retry-->>UI2: success or surfaced error
```
