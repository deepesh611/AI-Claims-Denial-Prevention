# HIPAA Privacy Rule — Complete Demo Implementation Guide

---

## Overview

This guide walks through a complete scenario-based demo of the HIPAA Privacy Rule using a web application. The demo follows a storytelling structure — from normal unprotected data, to the problem, to the solution (Privacy Rule in action).

**Tech Stack:**
- HTML + CSS + Vanilla JavaScript (no framework needed, runs in browser)
- No backend required — all data is simulated in-memory
- Single HTML file, self-contained

---

## Project Structure

```
hipaa-demo/
│
├── index.html          # Main entry — Normal Data view
├── problem.html        # What goes wrong without rules
├── phi.html            # What is PHI
├── hipaa.html          # HIPAA + Privacy Rule explanation
└── demo.html           # Scenario-based Privacy Rule demo
```

---

## Part 1 — Normal Data (index.html)

**Goal:** Show a basic user data table with zero restrictions. Anyone can see everything.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Normal Data</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }
    h1 { color: #333; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #4a90e2; color: white; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; background: white; }
    .note { margin-top: 20px; padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #4a90e2; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>

  <div class="nav">
    <a href="index.html">1. Normal Data</a>
    <a href="problem.html">2. The Problem</a>
    <a href="phi.html">3. What is PHI</a>
    <a href="hipaa.html">4. HIPAA</a>
    <a href="demo.html">5. Demo</a>
  </div>

  <h1>Normal Data — No Rules Applied</h1>
  <p>This is how data typically looks in any basic system. No access control. No restrictions. Anyone logged in can see everything.</p>

  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Email</th>
        <th>Phone</th>
        <th>Age</th>
        <th>City</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>001</td><td>Ravi Sharma</td><td>ravi@email.com</td><td>9876543210</td><td>34</td><td>Pune</td></tr>
      <tr><td>002</td><td>Priya Mehta</td><td>priya@email.com</td><td>9823456789</td><td>29</td><td>Mumbai</td></tr>
      <tr><td>003</td><td>Anil Desai</td><td>anil@email.com</td><td>9812345678</td><td>45</td><td>Delhi</td></tr>
    </tbody>
  </table>

  <div class="note">
    ⚠️ No login required. No role check. No audit log. Anyone can access this data freely.
  </div>

</body>
</html>
```

---

## Part 2 — The Problem (problem.html)

**Goal:** Show what happens when medical data is treated the same way — real consequences.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>The Problem</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }
    h1 { color: #c0392b; }
    .card { background: white; border-left: 5px solid #c0392b; padding: 20px; margin: 20px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .card h3 { margin: 0 0 8px; color: #c0392b; }
    .card p { margin: 0; color: #555; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #c0392b; color: white; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; background: white; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #4a90e2; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>

  <div class="nav">
    <a href="index.html">1. Normal Data</a>
    <a href="problem.html">2. The Problem</a>
    <a href="phi.html">3. What is PHI</a>
    <a href="hipaa.html">4. HIPAA</a>
    <a href="demo.html">5. Demo</a>
  </div>

  <h1>What Goes Wrong Without Rules</h1>
  <p>When medical data is handled like normal data — no restrictions, no accountability — this is what happens:</p>

  <div class="card">
    <h3>Case 1 — Employer Discrimination</h3>
    <p>A hospital receptionist shares a patient's HIV diagnosis with their employer. The patient gets fired. No rule was in place to prevent this.</p>
  </div>

  <div class="card">
    <h3>Case 2 — Data Sold for Profit</h3>
    <p>A clinic sells patient records including diagnoses and medications to a pharma company for targeted marketing. Patient never consented.</p>
  </div>

  <div class="card">
    <h3>Case 3 — Unauthorized Access</h3>
    <p>A nurse accesses a celebrity patient's records out of curiosity. No log exists. No one finds out. Privacy is violated with zero consequence.</p>
  </div>

  <div class="card">
    <h3>Case 4 — Wrong Person Gets Records</h3>
    <p>A hospital faxes test results to the wrong number. Patient's mental health diagnosis is now exposed to a stranger. No breach notification process exists.</p>
  </div>

  <h2 style="margin-top:40px;">Without Rules — Medical Data Looks Like This</h2>

  <table>
    <thead>
      <tr>
        <th>Patient</th>
        <th>Diagnosis</th>
        <th>Medication</th>
        <th>Insurance</th>
        <th>Who Can See This?</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>Ravi Sharma</td><td>HIV Positive</td><td>Antiretroviral</td><td>Star Health</td><td style="color:red;">EVERYONE</td></tr>
      <tr><td>Priya Mehta</td><td>Depression</td><td>Sertraline</td><td>HDFC Ergo</td><td style="color:red;">EVERYONE</td></tr>
      <tr><td>Anil Desai</td><td>Diabetes Type 2</td><td>Metformin</td><td>Max Bupa</td><td style="color:red;">EVERYONE</td></tr>
    </tbody>
  </table>

</body>
</html>
```

---

## Part 3 — What is PHI (phi.html)

**Goal:** Define PHI clearly with examples.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>What is PHI</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }
    h1 { color: #2c3e50; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; }
    .phi-item { background: #e8f4fd; border: 1px solid #b3d9f5; padding: 15px; border-radius: 6px; text-align: center; }
    .phi-item.not { background: #eafaf1; border-color: #a9dfbf; }
    .label { font-size: 11px; font-weight: bold; color: #888; margin-bottom: 4px; }
    .value { font-size: 15px; color: #2c3e50; font-weight: bold; }
    .section { margin-top: 40px; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #4a90e2; text-decoration: none; font-weight: bold; }
    .highlight { background: #ffeaa7; padding: 15px; border-radius: 6px; margin-top: 20px; }
  </style>
</head>
<body>

  <div class="nav">
    <a href="index.html">1. Normal Data</a>
    <a href="problem.html">2. The Problem</a>
    <a href="phi.html">3. What is PHI</a>
    <a href="hipaa.html">4. HIPAA</a>
    <a href="demo.html">5. Demo</a>
  </div>

  <h1>What is PHI — Protected Health Information</h1>
  <p>PHI is any information that can identify a patient AND relates to their health condition, treatment, or payment for healthcare.</p>

  <div class="highlight">
    <strong>Formula:</strong> Identity Information + Health/Treatment/Payment Information = PHI
  </div>

  <div class="section">
    <h2>The 18 HIPAA Identifiers (Examples)</h2>
    <div class="grid">
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Full Name</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Date of Birth</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Phone Number</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Email Address</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Social Security No.</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Medical Record No.</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">IP Address</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Geographic Data</div></div>
      <div class="phi-item"><div class="label">Identifier</div><div class="value">Photo / Biometrics</div></div>
    </div>
  </div>

  <div class="section">
    <h2>PHI vs Not PHI</h2>
    <div class="grid">
      <div class="phi-item"><div class="label">PHI ❌ Protected</div><div class="value">"Ravi Sharma has Diabetes"</div></div>
      <div class="phi-item not"><div class="label">Not PHI ✅ Safe</div><div class="value">"5% of patients have Diabetes"</div></div>
      <div class="phi-item"><div class="label">PHI ❌ Protected</div><div class="value">"Patient #001 prescribed Metformin"</div></div>
      <div class="phi-item not"><div class="label">Not PHI ✅ Safe</div><div class="value">"Metformin is used for Diabetes"</div></div>
    </div>
  </div>

</body>
</html>
```

---

## Part 4 — HIPAA & Privacy Rule (hipaa.html)

**Goal:** Explain HIPAA and the Privacy Rule requirements simply.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HIPAA Privacy Rule</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 40px; background: #f9f9f9; }
    h1 { color: #1a5276; }
    .rule-card { background: white; border-left: 5px solid #1a5276; padding: 20px; margin: 15px 0; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }
    .rule-card h3 { margin: 0 0 8px; color: #1a5276; }
    .rule-card p { margin: 0; color: #555; line-height: 1.6; }
    .nav { margin-bottom: 20px; }
    .nav a { margin-right: 15px; color: #4a90e2; text-decoration: none; font-weight: bold; }
    .cta { margin-top: 40px; text-align: center; }
    .cta a { background: #1a5276; color: white; padding: 14px 30px; border-radius: 6px; text-decoration: none; font-size: 16px; font-weight: bold; }
  </style>
</head>
<body>

  <div class="nav">
    <a href="index.html">1. Normal Data</a>
    <a href="problem.html">2. The Problem</a>
    <a href="phi.html">3. What is PHI</a>
    <a href="hipaa.html">4. HIPAA</a>
    <a href="demo.html">5. Demo</a>
  </div>

  <h1>HIPAA — Privacy Rule</h1>
  <p>HIPAA (Health Insurance Portability and Accountability Act, 1996) sets the standard for protecting sensitive patient data. The Privacy Rule specifically governs how PHI can be used and disclosed.</p>

  <h2>Key Requirements of the Privacy Rule</h2>

  <div class="rule-card">
    <h3>1. Minimum Necessary Standard</h3>
    <p>Only the minimum amount of PHI needed for a task should be accessed or shared. A receptionist does not need to see a patient's diagnosis to schedule an appointment.</p>
  </div>

  <div class="rule-card">
    <h3>2. Patient Authorization</h3>
    <p>PHI cannot be shared with third parties without explicit written consent from the patient — except for treatment, payment, or healthcare operations (TPO).</p>
  </div>

  <div class="rule-card">
    <h3>3. Patient Rights</h3>
    <p>Patients have the right to view their own records, request corrections, and receive an accounting of who their data was disclosed to.</p>
  </div>

  <div class="rule-card">
    <h3>4. Notice of Privacy Practices (NPP)</h3>
    <p>Every covered entity must provide patients with a written notice explaining how their PHI is used and what their rights are.</p>
  </div>

  <div class="rule-card">
    <h3>5. Disclosure Accounting</h3>
    <p>A log must be maintained of all disclosures of PHI made outside of TPO purposes. Patients can request this log.</p>
  </div>

  <div class="cta">
    <a href="demo.html">See the Privacy Rule in Action →</a>
  </div>

</body>
</html>
```

---

## Part 5 — Scenario Demo (demo.html)

**Goal:** Show all Privacy Rule requirements through a real hospital scenario.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>HIPAA Privacy Rule Demo</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f0f4f8; }

    /* Navigation */
    .nav { background: #1a5276; padding: 12px 40px; }
    .nav a { margin-right: 15px; color: #aed6f1; text-decoration: none; font-size: 13px; }
    .nav a:hover { color: white; }

    /* Layout */
    .container { display: grid; grid-template-columns: 240px 1fr 300px; gap: 0; min-height: 100vh; }

    /* Sidebar */
    .sidebar { background: #1a5276; color: white; padding: 20px; }
    .sidebar h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; color: #aed6f1; }
    .user-btn { display: block; width: 100%; padding: 10px 14px; margin-bottom: 8px; background: rgba(255,255,255,0.1); border: none; color: white; border-radius: 4px; cursor: pointer; text-align: left; font-size: 14px; }
    .user-btn:hover { background: rgba(255,255,255,0.2); }
    .user-btn.active { background: #2ecc71; color: white; }
    .current-user { margin-top: 20px; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; }
    .current-user .role { font-size: 11px; color: #aed6f1; }
    .current-user .name { font-size: 15px; font-weight: bold; margin-top: 2px; }

    /* Main content */
    .main { padding: 24px; }
    .main h2 { color: #1a5276; margin-bottom: 16px; }

    /* Patient cards */
    .patient-card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }
    .patient-card h3 { color: #2c3e50; margin-bottom: 10px; }
    .field { display: flex; margin-bottom: 6px; font-size: 14px; }
    .field-label { width: 160px; color: #888; flex-shrink: 0; }
    .field-value { color: #2c3e50; font-weight: 500; }
    .field-value.masked { color: #bbb; font-style: italic; }
    .access-btn { margin-top: 14px; padding: 8px 16px; background: #1a5276; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; margin-right: 8px; }
    .access-btn:hover { background: #154360; }
    .access-btn.danger { background: #c0392b; }
    .access-btn.danger:hover { background: #a93226; }
    .access-btn.success { background: #27ae60; }

    /* Alerts */
    .alert { padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; font-size: 14px; }
    .alert.blocked { background: #fdecea; border-left: 4px solid #c0392b; color: #c0392b; }
    .alert.allowed { background: #eafaf1; border-left: 4px solid #27ae60; color: #27ae60; }
    .alert.warning { background: #fef9e7; border-left: 4px solid #f39c12; color: #d68910; }

    /* Consent Modal */
    .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 100; align-items: center; justify-content: center; }
    .modal-overlay.active { display: flex; }
    .modal { background: white; padding: 30px; border-radius: 10px; width: 480px; max-width: 90%; }
    .modal h3 { color: #1a5276; margin-bottom: 14px; }
    .modal p { color: #555; font-size: 14px; line-height: 1.6; margin-bottom: 16px; }
    .modal-btns { display: flex; gap: 10px; }
    .modal-btns button { flex: 1; padding: 10px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold; }
    .btn-consent { background: #27ae60; color: white; }
    .btn-deny { background: #c0392b; color: white; }

    /* Audit log panel */
    .audit-panel { background: #2c3e50; color: white; padding: 20px; overflow-y: auto; }
    .audit-panel h3 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; color: #95a5a6; }
    .log-entry { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.07); font-size: 12px; }
    .log-entry .log-time { color: #95a5a6; margin-bottom: 3px; }
    .log-entry .log-action { color: #ecf0f1; }
    .log-entry.log-blocked { border-left: 3px solid #e74c3c; padding-left: 8px; }
    .log-entry.log-allowed { border-left: 3px solid #2ecc71; padding-left: 8px; }
    .log-entry.log-consent { border-left: 3px solid #f39c12; padding-left: 8px; }

    /* Tabs */
    .tabs { display: flex; gap: 4px; margin-bottom: 20px; }
    .tab { padding: 8px 18px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; background: #dce6f0; color: #1a5276; }
    .tab.active { background: #1a5276; color: white; }

    /* Amendment form */
    .amendment-form { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }
    .amendment-form textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; margin: 10px 0; }
    .amendment-form input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; margin: 6px 0; }

    /* NPP */
    .npp { background: white; border-radius: 8px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }
    .npp h3 { color: #1a5276; margin-bottom: 10px; }
    .npp p, .npp li { font-size: 14px; color: #555; line-height: 1.7; }
    .npp ul { padding-left: 20px; margin-top: 8px; }

    /* Scenario steps */
    .scenario-bar { background: white; padding: 16px 24px; border-bottom: 1px solid #ddd; }
    .scenario-bar h4 { color: #1a5276; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .steps { display: flex; gap: 8px; flex-wrap: wrap; }
    .step { padding: 6px 14px; background: #eaf0fb; border-radius: 20px; font-size: 12px; color: #1a5276; cursor: pointer; border: 2px solid transparent; }
    .step.active { border-color: #1a5276; font-weight: bold; }
    .step.done { background: #d5f5e3; color: #1e8449; }
  </style>
</head>
<body>

  <!-- Nav -->
  <div class="nav">
    <a href="index.html">1. Normal Data</a>
    <a href="problem.html">2. The Problem</a>
    <a href="phi.html">3. What is PHI</a>
    <a href="hipaa.html">4. HIPAA</a>
    <a href="demo.html">5. Demo</a>
  </div>

  <!-- Scenario Steps -->
  <div class="scenario-bar">
    <h4>Scenario Steps</h4>
    <div class="steps">
      <div class="step active" id="step1" onclick="setStep(1)">1. Doctor Views Records</div>
      <div class="step" id="step2" onclick="setStep(2)">2. Receptionist Blocked</div>
      <div class="step" id="step3" onclick="setStep(3)">3. Patient Views Own Records</div>
      <div class="step" id="step4" onclick="setStep(4)">4. Third-Party Share (Consent)</div>
      <div class="step" id="step5" onclick="setStep(5)">5. Patient Amendment Request</div>
      <div class="step" id="step6" onclick="setStep(6)">6. Notice of Privacy Practices</div>
    </div>
  </div>

  <!-- Main Layout -->
  <div class="container">

    <!-- Sidebar: User Switcher -->
    <div class="sidebar">
      <h3>Switch User</h3>
      <button class="user-btn active" onclick="switchUser('doctor')">👨‍⚕️ Dr. Amit (Doctor)</button>
      <button class="user-btn" onclick="switchUser('nurse')">👩‍⚕️ Neha (Nurse)</button>
      <button class="user-btn" onclick="switchUser('receptionist')">🧑‍💼 Raj (Receptionist)</button>
      <button class="user-btn" onclick="switchUser('patient')">🙍 Ravi (Patient)</button>
      <button class="user-btn" onclick="switchUser('admin')">🔐 Admin</button>

      <div class="current-user">
        <div class="role" id="current-role">ROLE: Doctor</div>
        <div class="name" id="current-name">Dr. Amit</div>
      </div>
    </div>

    <!-- Main Panel -->
    <div class="main">
      <div id="alert-box"></div>
      <div id="main-content"></div>
    </div>

    <!-- Audit Log -->
    <div class="audit-panel">
      <h3>Disclosure / Audit Log</h3>
      <div id="audit-log"></div>
    </div>

  </div>

  <!-- Consent Modal -->
  <div class="modal-overlay" id="consent-modal">
    <div class="modal">
      <h3>Patient Authorization Required</h3>
      <p>
        <strong>Requesting Party:</strong> Dr. Patel (External Specialist)<br><br>
        The following PHI is requested to be shared:<br>
        • Patient: Ravi Sharma<br>
        • Data: Diagnosis, Current Medications<br><br>
        Under HIPAA Privacy Rule, your explicit consent is required before this information can be shared with any party outside of your direct treatment team.
      </p>
      <div class="modal-btns">
        <button class="btn-consent" onclick="handleConsent(true)">✅ I Consent</button>
        <button class="btn-deny" onclick="handleConsent(false)">❌ I Deny</button>
      </div>
    </div>
  </div>

  <script>
    // --- Data ---
    const patients = [
      {
        id: "P001",
        name: "Ravi Sharma",
        dob: "15-Mar-1990",
        phone: "98765-43210",
        diagnosis: "Type 2 Diabetes",
        medication: "Metformin 500mg",
        insurance: "Star Health #SH4521",
        lastVisit: "12-Apr-2026",
        doctor: "Dr. Amit"
      },
      {
        id: "P002",
        name: "Priya Mehta",
        dob: "08-Jul-1995",
        phone: "98234-56789",
        diagnosis: "Depression",
        medication: "Sertraline 50mg",
        insurance: "HDFC Ergo #HD7823",
        lastVisit: "10-Apr-2026",
        doctor: "Dr. Amit"
      }
    ];

    // Role permissions: what fields each role can see
    const roleAccess = {
      doctor:       { name: true, dob: true, phone: true, diagnosis: true, medication: true, insurance: true, lastVisit: true },
      nurse:        { name: true, dob: true, phone: false, diagnosis: true, medication: true, insurance: false, lastVisit: true },
      receptionist: { name: true, dob: false, phone: true, diagnosis: false, medication: false, insurance: false, lastVisit: true },
      patient:      { name: true, dob: true, phone: true, diagnosis: true, medication: true, insurance: true, lastVisit: true },
      admin:        { name: true, dob: true, phone: true, diagnosis: true, medication: true, insurance: true, lastVisit: true }
    };

    const roleLabels = {
      doctor: "Doctor",
      nurse: "Nurse",
      receptionist: "Receptionist",
      patient: "Patient",
      admin: "Admin"
    };

    const userNames = {
      doctor: "Dr. Amit",
      nurse: "Neha",
      receptionist: "Raj",
      patient: "Ravi Sharma",
      admin: "Admin"
    };

    let currentUser = "doctor";
    let currentStep = 1;
    let logs = [];

    function getTime() {
      return new Date().toLocaleTimeString();
    }

    function addLog(action, type = "allowed") {
      logs.unshift({ time: getTime(), action, type });
      renderLog();
    }

    function renderLog() {
      const logEl = document.getElementById("audit-log");
      logEl.innerHTML = logs.map(l => `
        <div class="log-entry log-${l.type}">
          <div class="log-time">${l.time}</div>
          <div class="log-action">${l.action}</div>
        </div>
      `).join("");
    }

    function showAlert(msg, type) {
      document.getElementById("alert-box").innerHTML = `<div class="alert ${type}">${msg}</div>`;
      setTimeout(() => { document.getElementById("alert-box").innerHTML = ""; }, 4000);
    }

    function switchUser(role) {
      currentUser = role;
      document.querySelectorAll(".user-btn").forEach(b => b.classList.remove("active"));
      event.target.classList.add("active");
      document.getElementById("current-role").textContent = "ROLE: " + roleLabels[role];
      document.getElementById("current-name").textContent = userNames[role];
      renderStep(currentStep);
    }

    function setStep(n) {
      currentStep = n;
      document.querySelectorAll(".step").forEach((s, i) => {
        s.classList.remove("active");
        if (i < n - 1) s.classList.add("done");
        else s.classList.remove("done");
      });
      document.getElementById("step" + n).classList.add("active");
      renderStep(n);
    }

    function renderStep(n) {
      const content = document.getElementById("main-content");
      if (n === 1) renderPatientRecords(content);
      else if (n === 2) renderBlockedAccess(content);
      else if (n === 3) renderPatientView(content);
      else if (n === 4) renderThirdParty(content);
      else if (n === 5) renderAmendment(content);
      else if (n === 6) renderNPP(content);
    }

    function renderPatientRecords(content) {
      const access = roleAccess[currentUser];
      const canSeeAll = currentUser === "doctor" || currentUser === "admin";

      content.innerHTML = `
        <h2>Patient Records — Viewed as: ${userNames[currentUser]} (${roleLabels[currentUser]})</h2>
        ${patients.map(p => `
          <div class="patient-card">
            <h3>Patient: ${p.name} &nbsp; <span style="font-size:12px;color:#888;">ID: ${p.id}</span></h3>
            ${renderField("Date of Birth", p.dob, access.dob)}
            ${renderField("Phone", p.phone, access.phone)}
            ${renderField("Diagnosis", p.diagnosis, access.diagnosis)}
            ${renderField("Medication", p.medication, access.medication)}
            ${renderField("Insurance", p.insurance, access.insurance)}
            ${renderField("Last Visit", p.lastVisit, access.lastVisit)}
            <button class="access-btn" onclick="logAccess('${p.name}')">📋 Log Access</button>
          </div>
        `).join("")}
        <p style="font-size:13px;color:#888;margin-top:10px;">
          Fields marked as <span style="color:#bbb;font-style:italic;">— hidden —</span> are restricted for your role under the Minimum Necessary Standard.
        </p>
      `;
    }

    function renderField(label, value, allowed) {
      return `
        <div class="field">
          <div class="field-label">${label}</div>
          <div class="field-value ${allowed ? "" : "masked"}">${allowed ? value : "— hidden —"}</div>
        </div>
      `;
    }

    function logAccess(patientName) {
      addLog(`${userNames[currentUser]} (${roleLabels[currentUser]}) accessed records of ${patientName}`, "allowed");
      showAlert(`✅ Access logged: ${userNames[currentUser]} accessed ${patientName}'s record`, "allowed");
    }

    function renderBlockedAccess(content) {
      currentUser = "receptionist";
      document.querySelectorAll(".user-btn").forEach((b, i) => {
        b.classList.remove("active");
        if (i === 2) b.classList.add("active");
      });
      document.getElementById("current-role").textContent = "ROLE: Receptionist";
      document.getElementById("current-name").textContent = "Raj";

      const access = roleAccess["receptionist"];
      content.innerHTML = `
        <h2>Receptionist Tries to Access Full Medical Records</h2>
        <div class="alert warning">⚠️ Receptionist role only needs name, phone, and last visit date to schedule appointments. Diagnosis and medication are restricted — Minimum Necessary Standard applied.</div>
        ${patients.slice(0, 1).map(p => `
          <div class="patient-card">
            <h3>Patient: ${p.name}</h3>
            ${renderField("Date of Birth", p.dob, access.dob)}
            ${renderField("Phone", p.phone, access.phone)}
            ${renderField("Diagnosis", p.diagnosis, access.diagnosis)}
            ${renderField("Medication", p.medication, access.medication)}
            ${renderField("Insurance", p.insurance, access.insurance)}
            ${renderField("Last Visit", p.lastVisit, access.lastVisit)}
          </div>
        `).join("")}
        <button class="access-btn danger" onclick="tryUnauthorizedAccess()">🚫 Try to Access Diagnosis</button>
      `;
      addLog("Raj (Receptionist) viewed patient record — diagnosis and medication fields automatically restricted", "allowed");
    }

    function tryUnauthorizedAccess() {
      addLog("Raj (Receptionist) attempted to access restricted diagnosis field — BLOCKED by Minimum Necessary Rule", "blocked");
      showAlert("🚫 Access Denied: Receptionist role does not have permission to view diagnosis. Minimum Necessary Standard enforced.", "blocked");
    }

    function renderPatientView(content) {
      currentUser = "patient";
      document.querySelectorAll(".user-btn").forEach((b, i) => {
        b.classList.remove("active");
        if (i === 3) b.classList.add("active");
      });
      document.getElementById("current-role").textContent = "ROLE: Patient";
      document.getElementById("current-name").textContent = "Ravi Sharma";

      const p = patients[0];
      content.innerHTML = `
        <h2>Patient Views Own Records</h2>
        <div class="alert allowed">✅ Under HIPAA Privacy Rule, patients have the right to access their own complete records.</div>
        <div class="patient-card">
          <h3>${p.name} — Your Medical Record</h3>
          ${renderField("Date of Birth", p.dob, true)}
          ${renderField("Phone", p.phone, true)}
          ${renderField("Diagnosis", p.diagnosis, true)}
          ${renderField("Medication", p.medication, true)}
          ${renderField("Insurance", p.insurance, true)}
          ${renderField("Last Visit", p.lastVisit, true)}
          <button class="access-btn success" onclick="patientViewLog()">👁 View Disclosure Log</button>
        </div>
      `;
      addLog("Ravi Sharma (Patient) accessed own medical records — full access granted (Patient Right)", "allowed");
    }

    function patientViewLog() {
      showAlert("📋 Disclosure log shown to patient. Patient can see all parties who accessed their records.", "allowed");
      addLog("Ravi Sharma (Patient) requested disclosure log — provided as per HIPAA Patient Rights", "consent");
    }

    function renderThirdParty(content) {
      content.innerHTML = `
        <h2>Third-Party Share Request — Consent Required</h2>
        <div class="alert warning">⚠️ Dr. Patel (External Specialist) is requesting access to Ravi Sharma's diagnosis and medication history. Under the Privacy Rule, explicit patient authorization is required for disclosures outside TPO.</div>
        <div class="patient-card">
          <h3>Share Request Details</h3>
          ${renderField("Requesting Party", "Dr. Patel — City Hospital", true)}
          ${renderField("Patient", "Ravi Sharma", true)}
          ${renderField("Data Requested", "Diagnosis + Medications", true)}
          ${renderField("Purpose", "Second Opinion Consultation", true)}
          <button class="access-btn" onclick="requestConsent()">📝 Request Patient Consent</button>
        </div>
      `;
      addLog("Dr. Amit initiated third-party share request to Dr. Patel — awaiting patient consent", "consent");
    }

    function requestConsent() {
      document.getElementById("consent-modal").classList.add("active");
    }

    function handleConsent(approved) {
      document.getElementById("consent-modal").classList.remove("active");
      if (approved) {
        addLog("Ravi Sharma CONSENTED to share PHI with Dr. Patel (City Hospital) — disclosure authorized", "allowed");
        showAlert("✅ Patient consented. PHI shared with Dr. Patel. Disclosure recorded in audit log.", "allowed");
      } else {
        addLog("Ravi Sharma DENIED consent to share PHI with Dr. Patel — disclosure blocked", "blocked");
        showAlert("🚫 Patient denied consent. PHI will NOT be shared. Denial recorded.", "blocked");
      }
    }

    function renderAmendment(content) {
      content.innerHTML = `
        <h2>Patient Amendment Request</h2>
        <div class="alert allowed">✅ Under HIPAA, patients can request corrections to inaccurate or incomplete records.</div>
        <div class="amendment-form">
          <h3>Submit Amendment Request</h3>
          <p style="font-size:13px;color:#888;margin:8px 0 16px;">Patient: Ravi Sharma &nbsp;|&nbsp; Record ID: P001</p>
          <label style="font-size:13px;color:#555;">Field to Correct</label>
          <input type="text" placeholder="e.g. Diagnosis" value="Diagnosis" />
          <label style="font-size:13px;color:#555;">Current (Incorrect) Value</label>
          <input type="text" placeholder="Current value in record" value="Type 2 Diabetes" />
          <label style="font-size:13px;color:#555;">Requested Correction</label>
          <input type="text" placeholder="What it should say" value="Pre-Diabetic (not Type 2)" />
          <label style="font-size:13px;color:#555;">Reason for Amendment</label>
          <textarea rows="3" placeholder="Explain why this amendment is needed...">Recent tests show I am pre-diabetic, not Type 2. I request this be corrected.</textarea>
          <button class="access-btn success" onclick="submitAmendment()">📨 Submit Amendment Request</button>
        </div>
      `;
      addLog("Ravi Sharma (Patient) viewed amendment request form — patient right exercised", "allowed");
    }

    function submitAmendment() {
      addLog("Ravi Sharma submitted amendment request: Diagnosis correction requested — under review by Dr. Amit", "consent");
      showAlert("✅ Amendment request submitted. Provider has 60 days to respond under HIPAA.", "allowed");
    }

    function renderNPP(content) {
      content.innerHTML = `
        <h2>Notice of Privacy Practices</h2>
        <div class="alert allowed">✅ Every covered entity must provide patients this notice explaining how their PHI is used and what rights they have.</div>
        <div class="npp">
          <h3>City General Hospital — Notice of Privacy Practices</h3>
          <p style="margin:10px 0;">This notice describes how medical information about you may be used and disclosed, and how you can get access to this information.</p>

          <h3 style="margin-top:20px;">How We Use Your Information</h3>
          <ul>
            <li><strong>Treatment:</strong> We share your information with doctors, nurses, and specialists involved in your care.</li>
            <li><strong>Payment:</strong> We may use your information to bill your insurance company.</li>
            <li><strong>Operations:</strong> We use your information for quality assessment and hospital management.</li>
          </ul>

          <h3 style="margin-top:20px;">Your Rights</h3>
          <ul>
            <li>Right to access your medical records</li>
            <li>Right to request corrections (amendments)</li>
            <li>Right to know who your records were shared with (disclosure accounting)</li>
            <li>Right to request restrictions on how your data is used</li>
            <li>Right to be notified if your data is breached</li>
          </ul>

          <h3 style="margin-top:20px;">We Will Not</h3>
          <ul>
            <li>Sell your health information</li>
            <li>Share your information with employers</li>
            <li>Use your information for marketing without your consent</li>
          </ul>

          <button class="access-btn success" style="margin-top:20px;" onclick="acknowledgeNPP()">✅ I Acknowledge Receipt of This Notice</button>
        </div>
      `;
      addLog("Patient presented with Notice of Privacy Practices — acknowledgement pending", "consent");
    }

    function acknowledgeNPP() {
      addLog("Ravi Sharma acknowledged receipt of Notice of Privacy Practices — HIPAA NPP requirement fulfilled", "allowed");
      showAlert("✅ NPP acknowledged and recorded. HIPAA requirement fulfilled.", "allowed");
    }

    // Initial render
    renderStep(1);
    addLog("Demo initialized — Dr. Amit (Doctor) logged in", "allowed");
  </script>

</body>
</html>
```

---

## How to Run

1. Create a folder called `hipaa-demo`
2. Create all 5 HTML files inside it with the code above
3. Open `index.html` in any browser
4. No server needed — works entirely offline

---

## Demo Walkthrough Script

| Step | What to Show | Privacy Rule Requirement |
|------|-------------|--------------------------|
| 1 | Normal data — no restrictions | Contrast (before HIPAA) |
| 2 | Problem — consequences of no rules | Why HIPAA exists |
| 3 | PHI definition | What is protected |
| 4 | HIPAA Privacy Rule explained | The rule itself |
| 5 | Doctor views records — full access | Authorized access |
| 6 | Receptionist blocked from diagnosis | Minimum Necessary Standard |
| 7 | Patient views own records | Patient Access Rights |
| 8 | Third-party share + consent modal | Patient Authorization |
| 9 | Patient requests amendment | Amendment Rights |
| 10 | Notice of Privacy Practices | NPP Requirement |

---

## What Each Scenario Demonstrates

- **Role-based field masking** → Minimum Necessary Standard
- **Consent modal before sharing** → Patient Authorization
- **Patient full record access** → Patient Rights
- **Amendment form** → Right to Correct Records
- **Disclosure/Audit log** → Accounting of Disclosures
- **NPP page** → Notice of Privacy Practices

Every major requirement of the HIPAA Privacy Rule is covered.
