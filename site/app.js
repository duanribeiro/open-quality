const pages = {
  "/": {
    title: "Open Quality",
    description: "Quality as Code for teams that want quality expectations to be explicit, reviewable, and executable.",
    render: renderLanding,
    landing: true,
  },
  "/docs": {
    title: "Introduction",
    description: "A portable language for making software quality explicit, reviewable, and executable.",
    render: renderDocsHome,
  },
  "/concepts": {
    title: "Concepts",
    description: "The ideas behind Quality as Code, contracts, resources, and validation.",
    render: renderConcepts,
  },
  "/quick-start": {
    title: "Quick start",
    description: "Install the CLI, validate the minimal contract, and inspect readiness.",
    render: renderQuickStart,
  },
  "/cli": {
    title: "CLI reference",
    description: "The command-line surface for validating, rendering, evaluating, planning, and applying contracts.",
    render: renderCli,
  },
  "/resources": {
    title: "Resources",
    description: "The building blocks of a Quality Contract and how they connect.",
    render: renderResources,
  },
  "/syntax": {
    title: "Syntax",
    description: "Authoring rules for YAML and JSON resources.",
    render: renderSyntax,
  },
  "/workflows": {
    title: "Workflows and stages",
    description: "Model dependencies, parallel phases, ownership, and decisions.",
    render: renderWorkflows,
  },
  "/metrics": {
    title: "Quality measures",
    description: "Define stable measurements, formulas, units, and observations.",
    render: renderMetrics,
  },
  "/evaluation": {
    title: "Evaluation",
    description: "Understand state snapshots, readiness, requirements, and stage checks.",
    render: renderEvaluation,
  },
  "/artifacts": {
    title: "Artifacts",
    description: "Connect quality decisions to the documents that support them.",
    render: renderArtifacts,
  },
  "/approvals": {
    title: "Roles and approvals",
    description: "Separate accountability from the rules that govern approval.",
    render: renderApprovals,
  },
  "/providers": {
    title: "Providers",
    description: "Use external systems without coupling the core contract to a vendor.",
    render: renderProviders,
  },
  "/versioning": {
    title: "Versioning",
    description: "Manage specification compatibility and contract history.",
    render: renderVersioning,
  },
};

const app = document.querySelector("#app");
const sidebar = document.querySelector("#sidebar");
const breadcrumbs = document.querySelector("#breadcrumbs");
const searchOverlay = document.querySelector("#search-overlay");
const searchInput = document.querySelector("#search-input");
const searchResults = document.querySelector("#search-results");
const themeButton = document.querySelector("#theme-button");
const menuButton = document.querySelector("#menu-button");

function code(content) {
  return `<pre><code>${content}</code></pre>`;
}

function pageFrame(page, content) {
  return `
    <article class="page">
      <header class="page-header">
        <p class="eyebrow">Open Quality / Documentation</p>
        <h1>${page.title}</h1>
        <p>${page.description}</p>
      </header>
      <div class="prose">${content}</div>
    </article>
  `;
}

function renderLanding() {
  return `
    <div class="landing-page">
      <nav class="landing-nav">
        <a class="landing-brand" href="#/" aria-label="Open Quality home">
          <span class="landing-brand-mark">OQ</span>
          <span>open quality</span>
        </a>
        <div class="landing-nav-links" id="landing-nav-links">
          <a href="#/docs">DOCS</a>
          <a href="#/concepts">CONCEPTS</a>
          <a href="https://github.com/duanribeiro/open-quality" target="_blank" rel="noreferrer">GITHUB <span aria-hidden="true">↗</span></a>
        </div>
        <div class="landing-nav-actions">
          <button class="landing-mode" id="landing-theme" type="button" aria-label="Toggle color theme">☼</button>
          <a class="landing-nav-cta" href="#/quick-start">READ THE DOCS <span aria-hidden="true">→</span></a>
          <button class="landing-menu" id="landing-menu" type="button" aria-label="Open navigation" aria-expanded="false">☰</button>
        </div>
      </nav>

      <header class="landing-hero">
        <div class="landing-hero-grid"></div>
        <div class="landing-hero-copy">
          <p class="landing-eyebrow"><span></span> the quality contract</p>
          <h1>Quality,<br /><em>declared.</em></h1>
          <p class="landing-lede">
            Open Quality turns software-quality expectations into portable,
            version-controlled artifacts that teams can review, validate, and
            connect to the tools they already use.
          </p>
          <div class="landing-hero-actions">
            <a class="landing-button landing-button-primary" href="#/quick-start">START BUILDING <span aria-hidden="true">→</span></a>
            <a class="landing-text-link" href="#/concepts">WHY QUALITY AS CODE <span aria-hidden="true">↗</span></a>
          </div>
        </div>
        <div class="landing-hero-terminal">
          <div class="landing-terminal-top">
            <span>payment-api / quality</span>
            <span class="landing-terminal-status"><i></i> contract ready</span>
          </div>
          <pre><span class="terminal-comment"># define the quality contract</span>
<span class="terminal-key">kind</span>: <span class="terminal-value">QualityContract</span>
<span class="terminal-key">metadata</span>:
  <span class="terminal-key">id</span>: <span class="terminal-value">payment-api</span>
<span class="terminal-key">spec</span>:
  <span class="terminal-key">workflow</span>: <span class="terminal-value">standard-release</span>
  <span class="terminal-key">quality</span>:
    - <span class="terminal-key">characteristic</span>: <span class="terminal-value">reliability</span>
      <span class="terminal-key">requirements</span>:
        - <span class="terminal-value">api-availability</span>

<span class="terminal-prompt">$</span> oq validate examples/minimal
<span class="terminal-success">PASS</span> Payment API</pre>
        </div>
      </header>

      <section class="landing-stats" aria-label="Open Quality facts">
        <div><strong>09</strong><span>core resource kinds</span></div>
        <div><strong>08</strong><span>target operators</span></div>
        <div><strong>00</strong><span>vendor lock-in</span></div>
        <div><strong>0.1</strong><span>experimental foundation</span></div>
      </section>

      <section class="landing-intro">
        <div class="landing-section-kicker">A shared language for quality</div>
        <div class="landing-intro-grid">
          <h2>Make the invisible<br /><span>reviewable.</span></h2>
          <div>
            <p>
              Quality decisions are often spread across tickets, pipeline
              scripts, dashboards, and conversations. Open Quality gives them a
              durable home: one contract that describes what matters and how it
              connects.
            </p>
            <a class="landing-text-link" href="#/resources">EXPLORE THE MODEL <span aria-hidden="true">→</span></a>
          </div>
        </div>
      </section>

      <section class="landing-contract">
        <div class="landing-section-kicker">One contract, many implementations</div>
        <div class="landing-contract-grid">
          <div class="landing-contract-copy">
            <h2>From expectation<br />to evidence.</h2>
            <p>
              A Quality Contract connects requirements to measures, stages to
              dependencies, and decisions to accountable roles. The core stays
              portable while implementations collect state and perform the work.
            </p>
            <div class="landing-mini-links">
              <a href="#/concepts"><span>01</span> Concepts <b>→</b></a>
              <a href="#/resources"><span>02</span> Resources <b>→</b></a>
              <a href="#/evaluation"><span>03</span> Evaluation <b>→</b></a>
            </div>
          </div>
          <div class="landing-flow" aria-label="Quality Contract flow diagram">
            <div class="flow-node flow-node-main"><span>PROJECT</span><strong>Quality Contract</strong><small>the entry point</small></div>
            <div class="flow-connector"></div>
            <div class="flow-row">
              <div class="flow-node"><span>EXPECT</span><strong>Requirements</strong><small>what good means</small></div>
              <div class="flow-node"><span>PROCESS</span><strong>Workflow</strong><small>how work moves</small></div>
              <div class="flow-node"><span>DECIDE</span><strong>Approvals</strong><small>who signs off</small></div>
            </div>
            <div class="flow-connector flow-connector-short"></div>
            <div class="flow-node flow-node-state"><span>IMPLEMENT</span><strong>Evidence & state</strong><small>what is true now</small></div>
          </div>
        </div>
      </section>

      <section class="landing-features">
        <div class="landing-section-kicker">Built for real repositories</div>
        <div class="landing-feature-grid">
          <article>
            <span class="feature-number">01</span>
            <h3>Declarative</h3>
            <p>Represent quality expectations in readable YAML or JSON, with strict schemas and stable references.</p>
          </article>
          <article>
            <span class="feature-number">02</span>
            <h3>Vendor-neutral</h3>
            <p>Keep the contract independent from Jira, GitHub, GitLab, OpenProject, or the next tool in your stack.</p>
          </article>
          <article>
            <span class="feature-number">03</span>
            <h3>Machine-checkable</h3>
            <p>Validate structure, semantics, dependency graphs, targets, artifacts, ownership, and approvals.</p>
          </article>
        </div>
      </section>

      <section class="landing-cta">
        <div>
          <p class="landing-eyebrow"><span></span> open quality / 0.1.0</p>
          <h2>Start with what<br /><em>matters.</em></h2>
        </div>
        <div>
          <p>Build a contract for your next change and make the quality bar part of the review.</p>
          <a class="landing-button landing-button-primary" href="#/quick-start">READ THE QUICK START <span aria-hidden="true">→</span></a>
        </div>
      </section>

      <footer class="landing-footer">
        <a class="landing-brand" href="#/"><span class="landing-brand-mark">OQ</span><span>open quality</span></a>
        <span>Quality as Code · GPL-3.0</span>
        <a href="https://github.com/duanribeiro/open-quality" target="_blank" rel="noreferrer">SOURCE ON GITHUB ↗</a>
      </footer>
    </div>
  `;
}

function renderDocsHome() {
  return `
    <section class="hero">
      <p class="eyebrow">Open Quality / Documentation</p>
      <h1>Build the quality contract.</h1>
      <p>
        Start with the model, then move into syntax, workflows, measurements,
        evaluation, and provider integrations.
      </p>
      <div class="hero-actions">
        <a class="button primary" href="#/quick-start">Start building <span aria-hidden="true">→</span></a>
        <a class="button secondary" href="#/concepts">Explore concepts</a>
      </div>
    </section>

    <section>
      <h2>Documentation paths</h2>
      <p class="section-intro">A focused path from your first contract to an implementation that can evaluate and apply it.</p>
      <div class="feature-grid">
        <a class="feature-card" href="#/concepts"><span class="feature-icon">01</span><h3>Understand the model</h3><p>Quality as Code, contracts, resources, references, and validation.</p></a>
        <a class="feature-card" href="#/quick-start"><span class="feature-icon">02</span><h3>Write your first contract</h3><p>Install the CLI, validate the example, and inspect readiness.</p></a>
        <a class="feature-card" href="#/cli"><span class="feature-icon">03</span><h3>Operate the CLI</h3><p>Render workflows, evaluate state, and plan provider changes.</p></a>
      </div>
    </section>
  `;
}

function renderConcepts() {
  return pageFrame(pages["/concepts"], `
    <h2>Quality as Code</h2>
    <p>
      Quality as Code expresses quality expectations and governance as
      declarative, reviewable, version-controlled artifacts. The contract becomes
      an explicit input to delivery instead of a rule hidden in a pipeline.
    </p>
    <h2>Quality Contract</h2>
    <p>
      A Quality Contract is the complete set of resources that describes quality
      for one project. Its <code>QualityContract</code> entry point organizes quality as
      characteristic → subcharacteristic → requirement.
    </p>
    ${code(`<span class="token-muted">QualityContract</span>
├── <span class="token-key">quality requirements</span> ── measures / artifacts
├── <span class="token-key">workflow</span> ── stages ── dependencies
└── <span class="token-key">roles</span> ── approval policies`)}
    <h2>Declaration versus execution</h2>
    <p>
      Open Quality defines what a team expects and how those expectations relate.
      An implementation decides how to execute a stage, collect a metric, store an
      approval, or connect a person to a role.
    </p>
    <div class="callout"><strong>Portable by design.</strong> The reference CLI adds a local state snapshot to demonstrate evaluation. That snapshot is implementation-specific, not part of the portable resource model.</div>
    <h2>Validation</h2>
    <p>
      Structural validation checks document shape with JSON Schema. Semantic
      validation checks relationships across documents, such as missing roles,
      invalid references, duplicate IDs, and cyclic stage dependencies.
    </p>
    <h2>Out of scope for 0.1</h2>
    <p>
      Test execution, deployment execution, provider provisioning, dashboards,
      persistence, certification, waivers, and scoring are intentionally left to
      implementations while the vocabulary is being tested.
    </p>
  `);
}

function renderQuickStart() {
  return pageFrame(pages["/quick-start"], `
    <h2>Install</h2>
    <p>Open Quality requires Python 3.10 or newer.</p>
    ${code(`python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"`)}
    <h2>Validate the example</h2>
    <p>The repository includes a complete contract for a payment API:</p>
    ${code(`oq validate examples/minimal`)}
    <div class="callout"><strong>What validation does.</strong> It checks schemas and relationships. It does not execute tests or call an external provider.</div>
    <h2>Render the workflow</h2>
    ${code(`oq graph --format both examples/minimal`)}
    <h2>Evaluate readiness</h2>
    <p>The bundled snapshot is at <code>examples/state.yaml</code> and is used automatically when evaluating the minimal contract.</p>
    ${code(`oq evaluate examples/minimal
oq status examples/minimal`)}
    <p>The example represents a ready contract. Change a metric, remove documentation, or set a stage to <code>pending</code> to explore a failing evaluation.</p>
    <h2>Create your own contract</h2>
    <p>Keep one resource per YAML file. Directory names are organizational; references use <code>metadata.id</code>.</p>
    ${code(`my-contract/
├── quality-contract.yaml
├── workflows/
├── stages/
├── quality-requirements/
├── quality-measures/
├── artifacts/
├── roles/
└── approval-policies/`)}
  `);
}

function renderCli() {
  return pageFrame(pages["/cli"], `
    <p>The reference command-line interface is installed as <code>oq</code>.</p>
    <h2>Contract commands</h2>
    <h3><code>oq validate</code></h3>
    <p>Validate schemas, IDs, references, dependency cycles, targets, roles, artifacts, and approval policies.</p>
    ${code(`oq validate <quality-directory>`)}
    <h3><code>oq graph</code></h3>
    <p>Render a workflow as terminal text, Mermaid, or both.</p>
    ${code(`oq graph [--format ascii|mermaid|both] <quality-directory>`)}
    <h3><code>oq evaluate</code></h3>
    <p>Compare requirement targets and workflow state. It returns exit code <code>2</code> when the contract is valid but not ready.</p>
    ${code(`oq evaluate <quality-directory> [state.yaml]`)}
    <h3><code>oq status</code></h3>
    <p>Print a concise readiness summary and return <code>0</code> for every valid report.</p>
    ${code(`oq status <quality-directory> [state.yaml]`)}
    <h2>Provider commands</h2>
    <h3><code>oq plan</code></h3>
    <p>Preview external changes without writing to the provider.</p>
    ${code(`oq plan \\
  --target <target.yaml> \\
  [--provider-role <role>] \\
  <quality-directory>`)}
    <h3><code>oq apply</code></h3>
    <p>Apply provider changes using credentials from the environment.</p>
    ${code(`oq apply \\
  --target <target.yaml> \\
  [--provider-role <role>] \\
  <quality-directory>`)}
  `);
}

function renderResources() {
  return pageFrame(pages["/resources"], `
    <p>Every resource uses the same envelope and is identified by <code>kind</code>, not by its filename.</p>
    ${code(`<span class="token-key">specVersion</span>: <span class="token-string">"0.1"</span>
<span class="token-key">kind</span>: <span class="token-string">QualityRequirement</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">api-availability</span>
  <span class="token-key">name</span>: <span class="token-string">API availability</span>
<span class="token-key">spec</span>: {}`)}
    <h2>Core resources</h2>
    <table class="resource-table">
      <thead><tr><th>Resource</th><th>Describes</th></tr></thead>
      <tbody>
        <tr><td>QualityContract</td><td>The scope and entry point of a contract.</td></tr>
        <tr><td>QualityRequirement</td><td>A quality expectation and its acceptance target.</td></tr>
        <tr><td>Workflow</td><td>The stages that form a quality process.</td></tr>
        <tr><td>Stage</td><td>A phase of work, verification, or decision.</td></tr>
        <tr><td>QualityMeasure</td><td>The meaning, unit, and calculation of a measurement.</td></tr>
        <tr><td>QualityMeasureElement</td><td>A timestamped input observation.</td></tr>
        <tr><td>Artifact</td><td>A document used as quality evidence.</td></tr>
        <tr><td>Role</td><td>An accountable function used by ownership and approval.</td></tr>
        <tr><td>ApprovalPolicy</td><td>The rule for deciding whether approval is sufficient.</td></tr>
      </tbody>
    </table>
    <h2>References</h2>
    <p>References contain only the target resource ID and must resolve to the expected resource kind.</p>
    ${code(`<span class="token-key">spec</span>:
  <span class="token-key">workflow</span>: <span class="token-string">standard-release</span>
  <span class="token-key">metrics</span>:
    - <span class="token-string">unit-test-coverage</span>
  <span class="token-key">roles</span>:
    - <span class="token-string">software-engineer</span>`)}
  `);
}

function renderSyntax() {
  return pageFrame(pages["/syntax"], `
    <h2>Format</h2>
    <p>YAML is recommended for authoring. JSON is equivalent because resource documents map to the JSON data model used by the schemas.</p>
    <h2>Naming rules</h2>
    <ul>
      <li>Field names use <code>camelCase</code>.</li>
      <li>Resource IDs use lowercase kebab-case and are unique within a contract.</li>
      <li>References contain only the target resource ID.</li>
      <li>Percentages use values from 0 through 100.</li>
      <li>Durations use ISO 8601 strings where the schema permits them.</li>
    </ul>
    <h2>Operators</h2>
    <p>Version 0.1 uses named operators rather than free-form expressions:</p>
    ${code(`equals
notEquals
greaterThan
greaterThanOrEqual
lessThan
lessThanOrEqual
exists
approved`)}
    <div class="callout"><strong>Strict by default.</strong> Unknown fields are rejected in version 0.1 to catch spelling mistakes and keep implementations aligned.</div>
  `);
}

function renderWorkflows() {
  return pageFrame(pages["/workflows"], `
    <h2>Workflow and stages</h2>
    <p>A <code>Workflow</code> names the stages in a quality process. Dependencies live on each <code>Stage</code> through <code>dependsOn</code>.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">Workflow</span>
<span class="token-key">spec</span>:
  <span class="token-key">stages</span>:
    - <span class="token-string">technical-refinement</span>
    - <span class="token-string">continuous-integration</span>
    - <span class="token-string">release-approval</span>`)}
    <h2>Dependencies</h2>
    <p>Dependencies form a directed acyclic graph. Stages with the same satisfied dependencies may run in parallel; list order does not imply sequential execution.</p>
    ${code(`<span class="token-muted">technical-refinement</span>
├── <span class="token-key">continuous-integration</span>
└── <span class="token-key">security-review</span>
    └── <span class="token-key">release-approval</span>`)}
    <h2>Stage capabilities</h2>
    <p>Stages may declare an environment, review scope, owners, documentation, and an approval policy. Version 0.1 describes the process but does not define how stages start, retry, timeout, or persist runtime state.</p>
  `);
}

function renderMetrics() {
  return pageFrame(pages["/metrics"], `
    <h2>QualityMeasure</h2>
    <p>A <code>QualityMeasure</code> gives a stable name to a measurement and defines its unit or calculation.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">QualityMeasure</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">unit-test-coverage</span>
<span class="token-key">spec</span>:
  <span class="token-key">unit</span>: <span class="token-string">percent</span>
  <span class="token-key">sourceHint</span>: <span class="token-string">Coverage report from CI.</span>`)}
    <h2>QualityMeasureElement</h2>
    <p>Elements store the inputs to a measurement function. New observations are appended so history remains available.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">QualityMeasureElement</span>
<span class="token-key">spec</span>:
  <span class="token-key">unit</span>: <span class="token-string">lines</span>
  <span class="token-key">measurementMethod</span>: <span class="token-string">manual-entry</span>
  <span class="token-key">measurements</span>:
    - <span class="token-key">value</span>: <span class="token-string">850</span>
      <span class="token-key">measuredAt</span>: <span class="token-string">"2026-08-01T00:00:00Z"</span>`)}
    <div class="callout"><strong>Meaning versus collection.</strong> A source hint is descriptive only. It does not create a dependency on a provider.</div>
  `);
}

function renderEvaluation() {
  return pageFrame(pages["/evaluation"], `
    <p>The reference CLI evaluates a contract against an implementation-specific <code>state.yaml</code> snapshot.</p>
    ${code(`<span class="token-key">metrics</span>:
  <span class="token-key">unit-test-coverage</span>: <span class="token-string">85</span>
<span class="token-key">stages</span>:
  <span class="token-key">continuous-integration</span>: <span class="token-string">completed</span>
<span class="token-key">approvals</span>:
  <span class="token-key">code-review-approval</span>:
    - <span class="token-string">software-engineer</span>
<span class="token-key">documentation</span>:
  <span class="token-key">technical-design</span>: <span class="token-string">true</span>`)}
    <h2>Requirement checks</h2>
    <p>A requirement passes when every referenced target is satisfied and every required artifact is present.</p>
    <h2>Stage checks</h2>
    <p>A stage passes when its state is <code>completed</code>, its documentation is present, and its approval policy is satisfied.</p>
    <h2>Exit codes</h2>
    <ul>
      <li><code>0</code>: the contract is ready.</li>
      <li><code>1</code>: an input or operational error occurred.</li>
      <li><code>2</code>: the contract is valid but the state is not ready.</li>
    </ul>
  `);
}

function renderArtifacts() {
  return pageFrame(pages["/artifacts"], `
    <p>An <code>Artifact</code> represents documentation used to support a quality decision, such as a PRD, BRD, or technical design.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">Artifact</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">technical-design</span>
<span class="token-key">spec</span>:
  <span class="token-key">category</span>: <span class="token-string">documentation</span>
  <span class="token-key">externalLink</span>: <span class="token-string">https://docs.example.com/design</span>
  <span class="token-key">required</span>: <span class="token-string">true</span>`)}
    <p>Artifacts are referenced by the <code>documentation</code> field of a project, requirement, or stage. The document itself remains externally stored and governed by its own access controls.</p>
  `);
}

function renderApprovals() {
  return pageFrame(pages["/approvals"], `
    <p>Ownership and approval are distinct. A stage owner identifies accountability; an <code>ApprovalPolicy</code> defines who must approve.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">ApprovalPolicy</span>
<span class="token-key">spec</span>:
  <span class="token-key">strategy</span>: <span class="token-string">all</span>
  <span class="token-key">approvers</span>:
    - <span class="token-string">quality-lead</span>
    - <span class="token-string">engineering-manager</span>`)}
    <h2>Strategies</h2>
    <ul>
      <li><code>all</code>: every listed role approves.</li>
      <li><code>any</code>: at least one listed role approves.</li>
      <li><code>minimum</code>: a declared number of listed roles approves.</li>
    </ul>
    <div class="callout"><strong>Use roles, not people.</strong> Implementations map stable roles to identities so contracts do not change when staffing changes.</div>
    <p>Version 0.1 does not define ordered approvals, delegation, separation of duties, expiry, or waivers.</p>
  `);
}

function renderProviders() {
  return pageFrame(pages["/providers"], `
    <p>The Quality Contract stays provider-neutral. Provider configuration lives alongside a <code>QualityContract</code> and is selected by a provider role.</p>
    ${code(`<span class="token-key">providers</span>:
  <span class="token-key">workManagement</span>:
    <span class="token-key">provider</span>: <span class="token-string">openproject</span>
    <span class="token-key">config</span>:
      <span class="token-key">baseURL</span>: <span class="token-string">http://localhost:8080</span>`)}
    <h2>Supported adapters</h2>
    <p>The reference implementation includes OpenProject, Jira Cloud, GitHub, and GitLab adapters.</p>
    <h2>Plan before apply</h2>
    ${code(`oq plan \\
  --target examples/minimal/quality-contract.yaml \\
  --provider-role workManagement \\
  examples/minimal`)}
    <p>Credentials are never declared in provider YAML. They are read from environment variables by the selected adapter.</p>
  `);
}

function renderVersioning() {
  return pageFrame(pages["/versioning"], `
    <h2>Specification version</h2>
    <p>Every resource declares the specification family used to interpret it:</p>
    ${code(`<span class="token-key">specVersion</span>: <span class="token-string">"0.1"</span>`)}
    <p>Patch releases clarify or fix the current schema. Experimental minor releases may introduce breaking changes and use a new <code>specVersion</code> family.</p>
    <h2>Contract history</h2>
    <p>Contract evolution is normally tracked by source control. A user-defined release label may remain outside the core metadata until interoperability requires one.</p>
    <h2>Before 1.0</h2>
    <p>Breaking changes include release notes and updated examples. Migration documents and converters will be defined as the specification approaches its first stable compatibility commitment.</p>
  `);
}

function currentPath() {
  const hash = window.location.hash.replace(/^#/, "");
  return hash.split("?")[0] || "/";
}

function navigate() {
  const path = currentPath();
  const page = pages[path] || pages["/"];
  document.body.classList.toggle("is-landing", Boolean(page.landing));
  app.innerHTML = page.render();
  app.focus({ preventScroll: true });
  document.title = `${page.title} · Open Quality`;
  breadcrumbs.innerHTML = `<span>Open Quality</span><span class="breadcrumb-separator">/</span><strong>${page.title}</strong>`;
  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("active", link.dataset.route === path);
  });
  sidebar.classList.remove("open");
  if (page.landing) {
    bindLandingActions();
  }
  window.scrollTo(0, 0);
}

function bindLandingActions() {
  const landingTheme = document.querySelector("#landing-theme");
  const landingMenu = document.querySelector("#landing-menu");
  const landingLinks = document.querySelector("#landing-nav-links");
  if (landingTheme) {
    landingTheme.textContent = document.documentElement.dataset.theme === "dark" ? "☾" : "☼";
  }
  landingTheme?.addEventListener("click", () => {
    setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
    landingTheme.textContent = document.documentElement.dataset.theme === "dark" ? "☾" : "☼";
  });
  landingMenu?.addEventListener("click", () => {
    const open = landingLinks.classList.toggle("open");
    landingMenu.setAttribute("aria-expanded", String(open));
  });
}

function openSearch() {
  searchOverlay.hidden = false;
  searchInput.value = "";
  renderSearchResults("");
  window.setTimeout(() => searchInput.focus(), 0);
}

function closeSearch() {
  searchOverlay.hidden = true;
}

function renderSearchResults(query) {
  const normalized = query.trim().toLowerCase();
  const matches = Object.entries(pages).filter(([path, page]) => {
    const content = `${page.title} ${page.description} ${path}`.toLowerCase();
    return !normalized || content.includes(normalized);
  });
  if (!matches.length) {
    searchResults.innerHTML = `<div class="empty-search">No pages matched “${query}”.</div>`;
    return;
  }
  searchResults.innerHTML = matches
    .map(([path, page]) => `<a class="search-result" href="#${path}"><strong>${page.title}</strong><span>${page.description}</span></a>`)
    .join("");
}

function setTheme(theme) {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem("open-quality-theme", theme);
  themeButton.textContent = theme === "dark" ? "☾" : "☼";
}

window.addEventListener("hashchange", navigate);
document.querySelector("#search-trigger").addEventListener("click", openSearch);
document.querySelector("#search-close").addEventListener("click", closeSearch);
menuButton.addEventListener("click", () => sidebar.classList.toggle("open"));
themeButton.addEventListener("click", () => {
  setTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
});
searchInput.addEventListener("input", (event) => renderSearchResults(event.target.value));
searchOverlay.addEventListener("click", (event) => {
  if (event.target === searchOverlay) closeSearch();
});
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    openSearch();
  }
  if (event.key === "Escape" && !searchOverlay.hidden) closeSearch();
});

setTheme(localStorage.getItem("open-quality-theme") || "dark");
navigate();
