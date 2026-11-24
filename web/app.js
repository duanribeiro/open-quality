const pages = {
  "/": {
    title: "Open Quality",
    description: "Quality as Code for teams that want quality expectations to be explicit, reviewable, and executable.",
    render: renderLanding,
    landing: true,
  },
  "/quick-start": {
    title: "Quick start",
    description: "Install the CLI, create a contract with oq init, and add roles and team members.",
    render: renderQuickStart,
  },
  "/cli": {
    title: "CLI reference",
    description: "Initialize, add resources and team members, validate, evaluate, plan, and apply contracts.",
    keywords: "oq init oq add characteristic documentation metrics workflow role team",
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
    title: "Quality Characteristics",
    description: "Connect characteristics and subcharacteristics to requirements, quality measures, and measurement elements using ISO SQuaRE concepts.",
    keywords: "ISO IEC SQuaRE 25010 25019 25020 25021 25023 25030 QualityMeasure QualityMeasureElement availability reliability",
    render: renderMetrics,
  },
  "/evaluation": {
    title: "Evaluation",
    description: "Understand state snapshots, readiness, requirements, and stage checks.",
    render: renderEvaluation,
  },
  "/artifacts": {
    title: "Documentation",
    description: "Connect quality decisions to the documents that support them.",
    render: renderDocumentation,
  },
  "/approvals": {
    title: "Roles and approvals",
    description: "Separate accountability from the rules that govern approval.",
    render: renderApprovals,
  },
  "/team": {
    title: "Team and roles",
    description: "Associate people by email with one or more contract roles using team, oq add role, and oq add team.",
    render: renderTeam,
  },
  "/providers": {
    title: "Providers",
    description: "Use external systems without coupling the core contract to a vendor.",
    keywords: "OpenProject GitHub Projects Jira Cloud Kanban credentials members projectKey",
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
          <a href="#/quick-start">DOCS</a>
          <a href="https://github.com/duanribeiro/open-quality" target="_blank" rel="noreferrer">GITHUB <span aria-hidden="true">↗</span></a>
        </div>
        <div class="landing-nav-actions">
          <button class="landing-mode" id="landing-theme" type="button" aria-label="Toggle color theme">☼</button>
          <a class="landing-nav-cta" href="#/quick-start">READ THE DOCS <span aria-hidden="true">→</span></a>
          <button class="landing-menu" id="landing-menu" type="button" aria-label="Open navigation" aria-expanded="false">☰</button>
        </div>
      </nav>

      <header class="landing-hero">
        <div class="landing-hero-copy">
          <p class="landing-eyebrow"><span></span> the quality contract</p>
          <h1>Software Quality,<br /><em>declared.</em></h1>
          <p class="landing-lede">
            Open Quality keeps software-quality expectations in the project's
            own repository as version-controlled files that teams can review,
            validate, and connect to the tools they already use.
          </p>
          <div class="landing-hero-actions">
            <a class="landing-button landing-button-primary" href="#/quick-start">START BUILDING <span aria-hidden="true">→</span></a>
            <a class="landing-text-link" href="#/resources">WHY QUALITY AS CODE <span aria-hidden="true">↗</span></a>
          </div>
        </div>
        <div class="landing-hero-terminal">
          <div class="landing-terminal-top">
            <span>payment-api / .quality</span>
            <span class="landing-terminal-status"><i></i> contract ready</span>
          </div>
          <pre><span class="terminal-key">kind</span>: <span class="terminal-value">QualityContract</span>
<span class="terminal-key">metadata</span>:
  <span class="terminal-key">id</span>: <span class="terminal-value">payment-api</span>
  <span class="terminal-key">name</span>: <span class="terminal-value">Payment API</span>

<span class="terminal-comment"># Documentation resources to this project</span>
<span class="terminal-key">docs</span>:
  - <span class="terminal-value">technical-design</span>

<span class="terminal-comment"># Team members and their assigned roles</span>
<span class="terminal-key">team</span>:
  - <span class="terminal-key">email</span>: <span class="terminal-value">engineer@example.com</span>
    <span class="terminal-key">roles</span>:
      - <span class="terminal-value">software-engineer</span>
  - <span class="terminal-key">email</span>: <span class="terminal-value">lead@example.com</span>
    <span class="terminal-key">roles</span>:
      - <span class="terminal-value">quality-lead</span>
      - <span class="terminal-value">engineering-manager</span>

<span class="terminal-comment"># Predefined quality characteristics, based on <a href="https://pt.wikipedia.org/wiki/ISO/IEC_25000" target="_blank" rel="noreferrer">ISO models</a></span>
<span class="terminal-key">quality</span>:
  <span class="terminal-key">characteristics</span>:
    - <span class="terminal-key">characteristic</span>: <span class="terminal-value">reliability</span>
      <span class="terminal-key">subcharacteristics</span>:
        - <span class="terminal-key">subcharacteristic</span>: <span class="terminal-value">availability</span>
          <span class="terminal-key">requirements</span>: [<span class="terminal-value">api-availability-greater-than-99%</span>]
    - <span class="terminal-key">characteristic</span>: <span class="terminal-value">maintainability</span>
      <span class="terminal-key">subcharacteristics</span>:
        - <span class="terminal-key">subcharacteristic</span>: <span class="terminal-value">testability</span>
          <span class="terminal-key">requirements</span>: [<span class="terminal-value">unit-test-coverage-greater-than-90%</span>]

<span class="terminal-comment"># Work-management provider settings</span>
<span class="terminal-key">workManagement</span>:
  <span class="terminal-key">workflow</span>: <span class="terminal-value">standard-release</span>
  <span class="terminal-key">provider</span>: <span class="terminal-value">github</span>
  <span class="terminal-key">config</span>:
    <span class="terminal-key">owner</span>: <span class="terminal-value">duanribeiro</span>
    <span class="terminal-key">ownerType</span>: <span class="terminal-value">user</span>
    <span class="terminal-key">project</span>: <span class="terminal-value">Payment API Quality</span>

<span class="terminal-comment"># Source-control provider settings</span>
<span class="terminal-key">sourceControl</span>:
  <span class="terminal-key">provider</span>: <span class="terminal-value">github</span>
  <span class="terminal-key">config</span>:
    <span class="terminal-key">owner</span>: <span class="terminal-value">duanribeiro</span>
    <span class="terminal-key">ownerType</span>: <span class="terminal-value">user</span>
    <span class="terminal-key">repository</span>: <span class="terminal-value">payment-api</span>
</pre>
        </div>
      </header>

      <section class="landing-features">
        <div class="landing-feature-group">
          <div class="landing-section-kicker">Grounded in quality engineering</div>
          <div class="landing-feature-grid">
            <article>
              <span class="feature-number">01</span>
              <h3>Shift left</h3>
              <p>Define quality expectations while the contract is still a proposal, not after a feature has already shipped.</p>
            </article>
            <article>
              <span class="feature-number">02</span>
              <h3>ISO/IEC 25000 (SQuaRE)</h3>
              <p>Characteristics, subcharacteristics, and measures follow the SQuaRE series, so quality stays comparable across projects.</p>
            </article>
            <article>
              <span class="feature-number">03</span>
              <h3>Accountability by design</h3>
              <p>Every requirement traces to an owner, an approval policy, and the measure that proves it, not just a checklist.</p>
            </article>
          </div>
        </div>
        <div class="landing-feature-group">
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
              <p>Validate structure, semantics, dependency graphs, targets, documentation references, ownership, and approvals.</p>
            </article>
          </div>
        </div>
      </section>

      <section class="landing-contract">
        <div class="landing-section-kicker">One contract, many implementations</div>
        <div class="landing-contract-grid">
          <div class="landing-contract-copy">
            <h2>From expectation<br />to evidence.</h2>
            <p>
              A Quality Contract defines one hierarchy that registers every
              quality resource in a project: roles, team members,
              documentation, and provider settings at the root, down to the
              characteristics and subcharacteristics that classify each
              requirement.
            </p>
            <div class="landing-mini-links">
              <a href="#/resources"><span>01</span> Resources <b>→</b></a>
              <a href="#/evaluation"><span>02</span> Evaluation <b>→</b></a>
            </div>
          </div>
          <div class="landing-flow" aria-label="Quality Contract structure">
            <div class="flow-node flow-node-main"><span>PROJECT</span><strong>Quality Contract</strong><small>the entry point</small></div>
            <div class="flow-connector"></div>
            <ul class="contract-tree">
              <li class="tree-item">
                <div class="tree-label">team</div>
                <div class="tree-child">roles</div>
              </li>
              <li class="tree-item"><div class="tree-label">docs</div></li>
              <li class="tree-item"><div class="tree-label">workManagement</div></li>
              <li class="tree-item"><div class="tree-label">sourceControl</div></li>
              <li class="tree-item tree-item-wide">
                <div class="tree-label">quality</div>
                <div class="tree-child">
                  <div class="tree-label">characteristics / subcharacteristics</div>
                  <div class="tree-child">quality requirements</div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section class="landing-cta">
        <div>
          <p class="landing-eyebrow"><span></span> open quality / 0.1.0</p>
          <h2>Start with quality,<br /><em>not end with it.</em></h2>
        </div>
        <div>
          <p>Build a contract before the first line of code, so quality is part of the process from day one, not a check at the end.</p>
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

function renderQuickStart() {
  return pageFrame(pages["/quick-start"], `
    <div class="callout"><p>This quick start takes you from an empty directory to a validated Quality Contract, then walks the complete example in the repository through rendering, evaluation, and status.</p></div>

    <div class="learn-box">
      <p class="learn-box-title">What you'll learn</p>
      <ul>
        <li>How to install the Open Quality CLI</li>
        <li>What roles, team, and quality characteristics mean and how they connect</li>
        <li>How to create a contract and add roles and team members</li>
        <li>How to add quality resources as you need them</li>
        <li>How to validate a contract, your own or the bundled example</li>
        <li>How to render a workflow graph</li>
        <li>How to evaluate readiness from a state snapshot</li>
      </ul>
    </div>

    <h2>Install the CLI</h2>
    <p>Install the published <a href="https://pypi.org/project/open-quality-cli/" target="_blank" rel="noreferrer">Open Quality CLI package on PyPI</a>. Python 3.10 or newer is required.</p>
    ${code(`pipx install open-quality-cli`)}
    <p><code>pipx</code> installs the CLI in an isolated environment. If you prefer <code>pip</code>, use a virtual environment:</p>
    ${code(`python3 -m venv .venv
source .venv/bin/activate
python -m pip install open-quality-cli`)}

    <h2>Understand the pieces</h2>
    <p>The next command creates a contract and asks you to add roles and team members. Before you run it, here is what each piece means and how they connect:</p>
    <ul>
      <li><strong>Quality Contract</strong> — the entry point document for one project. It keeps <code>team</code>, <code>docs</code>, provider settings, and <code>quality.characteristics</code> together at its root.</li>
      <li><strong>Role</strong> — an accountable function, such as <code>quality-lead</code> or <code>software-engineer</code>. You declare roles once; other resources reference them by ID.</li>
      <li><strong>Team</strong> — maps people, by email, to one or more existing roles. It records accountability; it does not grant permissions in GitHub, Jira, or any other provider by itself.</li>
      <li>
        <strong>Quality characteristic / subcharacteristic</strong> — a characteristic is a broad quality area, such as reliability; it organizes subcharacteristics, such as availability. These characteristics and subcharacteristics are not invented per project: they are predefined by the <a href="https://www.iso.org/standard/78176.html" target="_blank" rel="noreferrer">ISO/IEC 25000 (SQuaRE)</a> series, so you pick from the schema's supported vocabulary instead of naming your own.
        <table class="resource-table">
          <thead><tr><th>Characteristic</th><th>Subcharacteristics</th></tr></thead>
          <tbody>
            <tr><td>functional-suitability</td><td>functional-completeness, functional-correctness, functional-appropriateness</td></tr>
            <tr><td>performance-efficiency</td><td>time-behaviour, resource-utilization, capacity</td></tr>
            <tr><td>compatibility</td><td>co-existence, interoperability</td></tr>
            <tr><td>interaction-capability</td><td>learnability, operability, user-error-protection, self-descriptiveness</td></tr>
            <tr><td>reliability</td><td>availability, fault-tolerance, recoverability</td></tr>
            <tr><td>security</td><td>confidentiality, integrity, non-repudiation, authenticity</td></tr>
            <tr><td>maintainability</td><td>modularity, reusability, analysability, testability</td></tr>
            <tr><td>flexibility</td><td>adaptability, scalability, installability, replaceability</td></tr>
            <tr><td>safety</td><td>risk-identification, fail-safe, hazard-warning</td></tr>
          </tbody>
        </table>
      </li>
      <li><strong>Quality requirement</strong> — the concrete, measurable expectation under a subcharacteristic, such as 99.95% monthly availability. It references one or more quality measures, each with its own acceptance target.</li>
      <li><strong>Quality measure</strong> — defines the quantity being measured and a function that calculates it from quality measure elements. The same measure can support different requirements with different targets.</li>
      <li><strong>Quality measure element</strong> — a recorded input: a collection method plus one or more timestamped observations, used as an input to a measure's function.</li>
      <li><strong>Work management</strong> — the provider role that connects the contract to a project board. It manages the flow of software delivery work and is reflected in a Kanban board, where each column represents a stage the work moves through.</li>
      <li><strong>Source control</strong> — the provider role that connects the contract to the repository where the code lives.</li>
    </ul>

    <p>The diagram below shows how these pieces connect:</p>
    <div class="hierarchy-diagram">
      <svg viewBox="0 0 680 660" role="img" aria-labelledby="hierarchy-title hierarchy-desc">
        <title id="hierarchy-title">Quality contract hierarchy</title>
        <desc id="hierarchy-desc">The quality contract is the root. Its children are Team, Work management, Source control and Quality. Roles sits below Team, which maps people to roles. Quality contains Characteristics, which leads to a chain of Subcharacteristic, Requirement, Measure and Measure element.</desc>
        <rect class="h-root" x="227" y="28" width="220" height="56" rx="8"/>
        <text class="h-title" x="337" y="47" text-anchor="middle" dominant-baseline="central">Quality contract</text>
        <text class="h-sub" x="337" y="65" text-anchor="middle" dominant-baseline="central">one per project</text>
        <path class="h-line" d="M337 84V112M103 112H571M103 112V140M259 112V140M415 112V140M571 112V140"/>
        <rect class="h-box-a" x="30" y="140" width="146" height="64" rx="8"/>
        <text class="h-title" x="103" y="162" text-anchor="middle" dominant-baseline="central">Team</text>
        <text class="h-sub" x="103" y="182" text-anchor="middle" dominant-baseline="central">people by email</text>
        <path class="h-line h-dash" d="M103 204V240"/>
        <text class="h-sub" x="112" y="222" text-anchor="start" dominant-baseline="central">maps people to roles</text>
        <rect class="h-box-b" x="30" y="240" width="146" height="64" rx="8"/>
        <text class="h-title" x="103" y="262" text-anchor="middle" dominant-baseline="central">Roles</text>
        <text class="h-sub" x="103" y="282" text-anchor="middle" dominant-baseline="central">accountable functions</text>
        <rect class="h-box-a" x="186" y="140" width="146" height="64" rx="8"/>
        <text class="h-title" x="259" y="162" text-anchor="middle" dominant-baseline="central">Work management</text>
        <text class="h-sub" x="259" y="182" text-anchor="middle" dominant-baseline="central">project board</text>
        <rect class="h-box-a" x="342" y="140" width="146" height="64" rx="8"/>
        <text class="h-title" x="415" y="162" text-anchor="middle" dominant-baseline="central">Source control</text>
        <text class="h-sub" x="415" y="182" text-anchor="middle" dominant-baseline="central">code repository</text>
        <rect class="h-box-a" x="498" y="140" width="146" height="64" rx="8"/>
        <text class="h-title" x="571" y="162" text-anchor="middle" dominant-baseline="central">Quality</text>
        <text class="h-sub" x="571" y="182" text-anchor="middle" dominant-baseline="central">ISO/IEC 25000</text>
        <path class="h-line" d="M571 204V228M571 284V308M571 364V388"/>
        <path class="h-line h-dash" d="M571 444V468M571 524V548"/>
        <rect class="h-box-b" x="498" y="228" width="146" height="56" rx="8"/>
        <text class="h-title" x="571" y="247" text-anchor="middle" dominant-baseline="central">Characteristics</text>
        <text class="h-sub" x="571" y="265" text-anchor="middle" dominant-baseline="central">e.g. reliability</text>
        <rect class="h-box-b" x="498" y="308" width="146" height="56" rx="8"/>
        <text class="h-title" x="571" y="327" text-anchor="middle" dominant-baseline="central">Subcharacteristic</text>
        <text class="h-sub" x="571" y="345" text-anchor="middle" dominant-baseline="central">e.g. availability</text>
        <rect class="h-box-b" x="498" y="388" width="146" height="56" rx="8"/>
        <text class="h-title" x="571" y="407" text-anchor="middle" dominant-baseline="central">Requirement</text>
        <text class="h-sub" x="571" y="425" text-anchor="middle" dominant-baseline="central">e.g. 99.95% monthly</text>
        <rect class="h-box-b" x="498" y="468" width="146" height="56" rx="8"/>
        <text class="h-title" x="571" y="487" text-anchor="middle" dominant-baseline="central">Measure</text>
        <text class="h-sub" x="571" y="505" text-anchor="middle" dominant-baseline="central">quantity + function</text>
        <rect class="h-box-b" x="498" y="548" width="146" height="56" rx="8"/>
        <text class="h-title" x="571" y="567" text-anchor="middle" dominant-baseline="central">Measure element</text>
        <text class="h-sub" x="571" y="585" text-anchor="middle" dominant-baseline="central">recorded input</text>
        <text class="h-sub" x="578" y="216" dominant-baseline="central">has</text>
        <text class="h-sub" x="578" y="296" dominant-baseline="central">has</text>
        <text class="h-sub" x="578" y="376" dominant-baseline="central">has</text>
        <text class="h-sub" x="578" y="456" dominant-baseline="central">references</text>
        <text class="h-sub" x="578" y="536" dominant-baseline="central">calculated from</text>
        <path class="h-line" d="M40 630H72"/>
        <text class="h-sub" x="80" y="630" dominant-baseline="central">contains</text>
        <path class="h-line h-dash" d="M200 630H232"/>
        <text class="h-sub" x="240" y="630" dominant-baseline="central">references</text>
      </svg>
    </div>

    <h2>Create your own contract</h2>
    <p>With that vocabulary in place, initialize a contract, then add the roles and people who will own it:</p>
    ${code(`oq init
oq add [characteristic|documentation|metrics|workflow|role|team]
oq validate`)}
    <p><code>oq init</code> creates a contract, workflow, and stages in a new or empty <code>.quality</code> directory. It asks separately about work management and source control. Quality characteristics are optional; <code>quality.characteristics: []</code> is valid.</p>
    <p>Create roles first, then add people by email and select their roles. You can associate several roles with a person and add several people in one run.</p>

    <p>Keep one resource per YAML file. Directory names are organizational; references use <code>metadata.id</code>.</p>
    ${code(`.quality/
├── quality-contract.yaml
├── workflows/
├── stages/
├── quality-requirements/
├── quality-measures/
├── quality-measure-elements/
├── docs/
├── roles/
└── approval-policies/`)}

    <h2>Render the workflow</h2>
    ${code(`oq graph --format both examples/minimal`)}

  `);
}

function renderCli() {
  return pageFrame(pages["/cli"], `
    <p>The reference command-line interface is installed as <code>oq</code>.</p>
    <h2>Create and extend a contract</h2>
    <h3><code>oq init</code></h3>
    ${code(`oq init [quality-directory]`)}
    <p>Create a starter contract in a new or empty directory, defaulting to <code>.quality</code>. The wizard prompts for project details, optional providers, a workflow ID, and stage IDs. It creates sequential stage dependencies and keeps credentials in environment variables.</p>
    <h3><code>oq add</code></h3>
    ${code(`oq add characteristic [quality-directory]
oq add documentation [quality-directory]
oq add metrics [quality-directory]
oq add workflow [quality-directory]
oq add role [quality-directory]
oq add team [quality-directory]`)}
    <table class="resource-table">
      <thead><tr><th>Resource</th><th>Interactive behavior</th></tr></thead>
      <tbody>
        <tr><td>characteristic</td><td>Select characteristics and create their requirements, measures, and targets.</td></tr>
        <tr><td>documentation</td><td>Create a Documentation resource with an ID, name, absolute URL, required flag, and content type.</td></tr>
        <tr><td>metrics</td><td>Create a QualityMeasure resource. Add its ID to a QualityRequirement's qualityMeasures list to use it.</td></tr>
        <tr><td>workflow</td><td>Create a workflow and stages from comma-separated IDs; each stage depends on the previous one.</td></tr>
        <tr><td>role</td><td>Create roles/&lt;id&gt;.yaml for assignment to team members. Prompt for ID, name, optional description, and responsibilities separated by semicolons.</td></tr>
        <tr><td>team</td><td>Add people by email and select one or more existing roles by number or ID. Offer to add another person and preserve existing members.</td></tr>
      </tbody>
    </table>
    <p>All <code>oq add</code> commands default to <code>.quality</code>. Create roles before adding people. Existing resource files are protected against overwriting; resource IDs and team emails must be unique.</p>
    <h2>Contract commands</h2>
    <h3><code>oq validate</code></h3>
    <p>Validate schemas, IDs, references, dependency cycles, targets, roles, documentation references, and approval policies.</p>
    ${code(`oq validate [quality-directory]`)}
    <p>When the directory is omitted, validate <code>.quality</code> in the current working directory, matching <code>oq init</code> and <code>oq add</code>. Pass another directory explicitly, such as <code>oq validate examples/minimal</code>, when needed.</p>
    <h3><code>oq graph</code></h3>
    <p>Render a workflow as terminal text, Mermaid, or both.</p>
    ${code(`oq graph [--format ascii|mermaid|both] &lt;quality-directory&gt;`)}
    <h3><code>oq evaluate</code></h3>
    <p>Compare requirement targets and workflow state. It returns exit code <code>2</code> when the contract is valid but not ready.</p>
    ${code(`oq evaluate &lt;quality-directory&gt; [state.yaml]`)}
    <h3><code>oq status</code></h3>
    <p>Print a concise readiness summary and return <code>0</code> for every valid report.</p>
    ${code(`oq status &lt;quality-directory&gt; [state.yaml]`)}
    <h2>Provider commands</h2>
    <h3><code>oq plan</code></h3>
    <p>Preview external changes without writing to the provider.</p>
    ${code(`oq plan \\
  [--target &lt;target.yaml&gt;] \\
  [--provider-role &lt;role&gt;] \\
  [quality-directory]`)}
    <h3><code>oq apply</code></h3>
    <p>Apply provider changes using credentials from the environment.</p>
    ${code(`oq apply \\
  [--target &lt;target.yaml&gt;] \\
  [--provider-role &lt;role&gt;] \\
  [quality-directory]`)}
    <p>The default target is <code>.quality/quality-contract.yaml</code>. Without <code>--provider-role</code>, all configured providers run in YAML order. Use <code>--provider-role sourceControl</code> to run only repository provisioning. If omitted, the contract directory is inferred from the target file.</p>
  `);
}

function renderResources() {
  return pageFrame(pages["/resources"], `
    <p>Every resource uses the same envelope and is identified by <code>kind</code>, not by its filename.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">QualityRequirement</span>
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
        <tr><td>Documentation</td><td>A document used as quality evidence.</td></tr>
        <tr><td>Role</td><td>An accountable function used by ownership and approval.</td></tr>
        <tr><td>ApprovalPolicy</td><td>The rule for deciding whether approval is sufficient.</td></tr>
      </tbody>
    </table>
    <h2>References</h2>
    <p>References contain only the target resource ID and must resolve to the expected resource kind.</p>
    ${code(`<span class="token-key">quality</span>:
  <span class="token-key">characteristics</span>: []
<span class="token-key">docs</span>:
  - <span class="token-string">technical-design</span>
<span class="token-key">roles</span>:
  - <span class="token-string">software-engineer</span>`)}
    <h2>Team assignments</h2>
    <p>The optional <code>QualityContract.team</code> list sits at the document root, beside <code>docs</code>, <code>quality</code>, and provider roles. It maps each person's email to existing Role IDs. See <a href="#/team">Team and roles</a> for authoring and validation rules.</p>
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
    <h2>Contract fields and schemas</h2>
    <p><code>QualityContract</code> requires <code>kind</code>, <code>metadata</code>, and <code>quality.characteristics</code>; the characteristics list may be empty. <code>docs</code>, <code>team</code>, <code>workManagement</code>, and <code>sourceControl</code> also belong directly at the root. Role assignments belong inside each team member. Measures are referenced from each <code>QualityRequirement.spec.qualityMeasures</code>, not from <code>quality</code>.</p>
    <p>The schemas in <code>schema/v0.1/</code> use JSON Schema Draft 2020-12. <code>quality.schema.json</code> accepts any of the nine resource kinds. Cross-resource checks, including missing roles and duplicate team emails, run through <code>oq validate</code>.</p>
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
    - <span class="token-string">development</span>
    - <span class="token-string">code-review</span>
    - <span class="token-string">uat-deployment</span>
    - <span class="token-string">prd-deployment</span>`)}
    <h2>Dependencies</h2>
    <p>Dependencies form a directed acyclic graph. Stages with the same satisfied dependencies may run in parallel; list order does not imply sequential execution.</p>
    ${code(`<span class="token-muted">code-review</span>
└── <span class="token-key">uat-deployment</span>
    └── <span class="token-key">prd-deployment</span>`)}
    ${code(`<span class="token-key">kind</span>: <span class="token-string">Stage</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">uat-deployment</span>
  <span class="token-key">name</span>: <span class="token-string">UAT deployment</span>
<span class="token-key">spec</span>:
  <span class="token-key">description</span>: <span class="token-string">Deploy the release to UAT for acceptance validation.</span>
  <span class="token-key">environment</span>: <span class="token-string">uat</span>
  <span class="token-key">dependsOn</span>: [<span class="token-string">code-review</span>]`)}
    ${code(`<span class="token-key">kind</span>: <span class="token-string">Stage</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">prd-deployment</span>
  <span class="token-key">name</span>: <span class="token-string">PRD deployment</span>
<span class="token-key">spec</span>:
  <span class="token-key">description</span>: <span class="token-string">Deploy the approved release to production.</span>
  <span class="token-key">environment</span>: <span class="token-string">prd</span>
  <span class="token-key">dependsOn</span>: [<span class="token-string">uat-deployment</span>]`)}
    <h2>Stage capabilities</h2>
    <p><code>description</code> is optional. Stages may also declare an environment, review scope, owners, documentation, and an approval policy. Version 0.1 describes the process but does not define how stages start, retry, timeout, or persist runtime state.</p>
  `);
}

function renderMetrics() {
  return pageFrame(pages["/metrics"], `
    <h2>From a quality goal to measurable evidence</h2>
    <p>A characteristic identifies the aspect of quality you care about. A subcharacteristic narrows that aspect. A requirement defines the expected result, a quality measure defines how to quantify it, and quality measure elements record the observations used in that calculation.</p>
    <p>There is no <code>measures</code> list on <code>QualityContract.quality</code>. Each requirement declares its own measure references in <code>spec.qualityMeasures</code>, alongside its target.</p>
    ${code(`QualityContract.quality.characteristics
└── characteristic: reliability
    └── subcharacteristic: availability
        └── QualityRequirement: api-availability
            ├── target: at least 99.95 percent
            └── QualityMeasure: availability
                └── QualityMeasureElement inputs
                    ├── available-time
                    └── total-time`)}
    <h2>Characteristics</h2>
    <p>Characteristics organize quality requirements into broad areas. The Open Quality schema accepts the following product-quality identifiers. These short descriptions help you select an area; consult <a href="https://www.iso.org/standard/78176.html" target="_blank" rel="noreferrer">ISO/IEC 25010:2023</a> for the formal product model, which has nine characteristics and their subcharacteristics.</p>
    <table class="resource-table">
      <thead><tr><th>Characteristic</th><th>Quality concern</th></tr></thead>
      <tbody>
        <tr><td>functional-suitability</td><td>Functions meet the intended needs.</td></tr>
        <tr><td>performance-efficiency</td><td>Response time, resource use, and capacity.</td></tr>
        <tr><td>compatibility</td><td>Coexistence and interoperability with other systems.</td></tr>
        <tr><td>interaction-capability</td><td>People can understand and interact with the product.</td></tr>
        <tr><td>reliability</td><td>Dependable operation, availability, and recovery.</td></tr>
        <tr><td>security</td><td>Protection of information and access.</td></tr>
        <tr><td>maintainability</td><td>Analysis, modification, and testing of the product.</td></tr>
        <tr><td>flexibility</td><td>Adaptation, scaling, installation, and replacement.</td></tr>
        <tr><td>safety</td><td>Identification and control of hazards.</td></tr>
      </tbody>
    </table>
    <p>The schema also accepts <code>beneficialness</code>, <code>freedom-from-risk</code>, and <code>acceptability</code> for quality in use. This concerns outcomes for stakeholders in a specified context, rather than product properties alone. <a href="https://www.iso.org/standard/78177.html" target="_blank" rel="noreferrer">ISO/IEC 25019:2023</a> defines the separate quality-in-use model. Together these explain the twelve characteristic IDs accepted by Open Quality.</p>
    <h2>Subcharacteristics</h2>
    <p>Subcharacteristics make the quality concern more precise. For example, availability is one aspect of reliability, and testability is one aspect of maintainability. Declare them inside the selected characteristic in <code>QualityContract.quality</code>.</p>
    <table class="resource-table">
      <thead><tr><th>Characteristic</th><th>Example subcharacteristics</th><th>Possible evidence</th></tr></thead>
      <tbody>
        <tr><td>reliability</td><td>availability, fault-tolerance, recoverability</td><td>Available time, failure tests, recovery time.</td></tr>
        <tr><td>maintainability</td><td>modularity, analysability, testability</td><td>Dependency analysis and automated testing evidence.</td></tr>
        <tr><td>performance-efficiency</td><td>time-behaviour, resource-utilization, capacity</td><td>Latency, memory use, and supported workload.</td></tr>
      </tbody>
    </table>
    <p>Characteristics and subcharacteristics are classification fields, not separate resource kinds. Their identifiers come from the schema's supported vocabulary. A characteristic references requirements either through subcharacteristics or directly through <code>requirements</code>; it cannot use both forms in the same entry.</p>
    <h2>A complete availability example</h2>
    <h3>1. Classify the requirement in the contract</h3>
    ${code(`kind: QualityContract
metadata:
  id: payment-api
  name: Payment API
quality:
  characteristics:
    - characteristic: reliability
      subcharacteristics:
        - subcharacteristic: availability
          requirements:
            - api-availability`)}
    ${code(`workManagement:
  workflow: standard-release
  provider: github
  config:
    owner: example
    project: Payment API`)}
    <h3>2. Declare the requirement and its target</h3>
    <p>A <code>QualityRequirement</code> states the team's acceptance criterion and references a measure by ID. The threshold is a contract decision based on your context; it is not a universal ISO score.</p>
    ${code(`kind: QualityRequirement
metadata:
  id: api-availability
  name: API availability
spec:
  statement: The API must achieve at least 99.95% monthly availability.
  priority: critical
  qualityMeasures:
    - qualityMeasure: availability
      target:
        operator: greaterThanOrEqual
        value: 99.95
        unit: percent`)}
    <h2>QualityMeasure</h2>
    <p>A <code>QualityMeasure</code> defines the quantity you measure, its unit, and an optional measurement function. The function references <code>QualityMeasureElement</code> IDs as inputs. The acceptance target belongs to the requirement, allowing the same measure to support different expectations.</p>
    ${code(`kind: QualityMeasure
metadata:
  id: availability
  name: Monthly availability
spec:
  measurementFunction:
    expression: "(available-time / total-time) * 100"
    elements: [available-time, total-time]
  unit: percent
  sourceHint: Monthly service-level telemetry.`)}
    <h2>QualityMeasureElement</h2>
    <p>A <code>QualityMeasureElement</code> records a measured input: a collection method, an optional unit, and one or more numeric observations with timestamps. Append observations to retain history, and document their collection period so the inputs are comparable.</p>
    ${code(`kind: QualityMeasureElement
metadata:
  id: available-time
  name: Available time
spec:
  unit: seconds
  measurementMethod: manual-entry
  measurements:
    - value: 2591872
      measuredAt: "2026-08-01T00:00:00Z"`)}
    ${code(`kind: QualityMeasureElement
metadata:
  id: total-time
  name: Total time
spec:
  unit: seconds
  measurementMethod: manual-entry
  measurements:
    - value: 2592000
      measuredAt: "2026-08-01T00:00:00Z"`)}
    <p>For the same monthly observation period, these inputs produce approximately <code>99.9951%</code> availability, above the requirement's <code>99.95%</code> target. This is an illustrative contract calculation, not a prescribed ISO formula.</p>
    <h2>How this relates to ISO SQuaRE</h2>
    <p>SQuaRE stands for Systems and software Quality Requirements and Evaluation. The following mapping explains how Open Quality's resources organize these concepts; Open Quality does not reproduce the standards or claim that schema validation proves ISO conformity.</p>
    <table class="resource-table">
      <thead><tr><th>ISO reference</th><th>Purpose</th><th>Connection to Open Quality</th></tr></thead>
      <tbody>
        <tr><td><a href="https://www.iso.org/standard/78176.html" target="_blank" rel="noreferrer">ISO/IEC 25010:2023</a></td><td>Product quality model.</td><td>Characteristics and subcharacteristics classify product-quality requirements.</td></tr>
        <tr><td><a href="https://www.iso.org/standard/78177.html" target="_blank" rel="noreferrer">ISO/IEC 25019:2023</a></td><td>Quality-in-use model.</td><td>Quality-in-use categories describe stakeholder outcomes in a stated context.</td></tr>
        <tr><td><a href="https://www.iso.org/standard/72117.html" target="_blank" rel="noreferrer">ISO/IEC 25020:2019</a></td><td>Quality measurement framework.</td><td>Connects measurement definitions, inputs, and interpretation of results.</td></tr>
        <tr><td><a href="https://www.iso.org/standard/55477.html" target="_blank" rel="noreferrer">ISO/IEC 25021:2012</a></td><td>Guidance for quality measure elements.</td><td>QualityMeasureElement records the observations used as measure inputs.</td></tr>
        <tr><td><a href="https://www.iso.org/standard/35747.html" target="_blank" rel="noreferrer">ISO/IEC 25023:2016</a></td><td>Measures for evaluating product quality.</td><td>QualityMeasure defines a quantity or calculation; the contract selects its target.</td></tr>
        <tr><td><a href="https://www.iso.org/standard/72116.html" target="_blank" rel="noreferrer">ISO/IEC 25030:2019</a></td><td>Quality requirements framework.</td><td>QualityRequirement expresses the expected quality and acceptance criteria.</td></tr>
      </tbody>
    </table>
    <h2>Validate and evaluate with the CLI</h2>
    ${code(`oq add characteristic
oq validate
oq evaluate .quality state.yaml`)}
    <p>The CLI validates resource structure and references. Its current evaluator compares targets against values supplied in the runtime snapshot's <code>metrics</code> mapping; it does not execute <code>measurementFunction.expression</code> or derive values automatically from recorded elements. Your measurement process must calculate the result and supply it to the evaluator.</p>
    ${code(`metrics:
  availability: 99.9951`)}
    <p>This is only the metrics portion of a runtime snapshot; stage completion, documentation, and approvals also affect overall readiness. A <code>sourceHint</code> describes where measurements come from but does not automatically collect telemetry or invoke a provider.</p>
  `);
}

function renderEvaluation() {
  return pageFrame(pages["/evaluation"], `
    <p>The reference CLI evaluates a contract against an implementation-specific <code>state.yaml</code> snapshot.</p>
    ${code(`<span class="token-key">metrics</span>:
  <span class="token-key">unit-test-coverage</span>: <span class="token-string">85</span>
<span class="token-key">stages</span>:
  <span class="token-key">code-review</span>: <span class="token-string">completed</span>
  <span class="token-key">uat-deployment</span>: <span class="token-string">completed</span>
  <span class="token-key">prd-deployment</span>: <span class="token-string">completed</span>
<span class="token-key">approvals</span>:
  <span class="token-key">code-review-approval</span>:
    - <span class="token-string">software-engineer</span>
<span class="token-key">documentation</span>:
  <span class="token-key">technical-design</span>: <span class="token-string">true</span>`)}
    <h2>Requirement checks</h2>
    <p>A requirement passes when every referenced target is satisfied and every required documentation resource is present.</p>
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

function renderDocumentation() {
  return pageFrame(pages["/artifacts"], `
    <p>A <code>Documentation</code> resource represents material used to support a quality decision, such as a PRD, BRD, or technical design.</p>
    ${code(`<span class="token-key">kind</span>: <span class="token-string">Documentation</span>
<span class="token-key">metadata</span>:
  <span class="token-key">id</span>: <span class="token-string">technical-design</span>
<span class="token-key">spec</span>:
  <span class="token-key">externalLink</span>: <span class="token-string">https://docs.example.com/design</span>
  <span class="token-key">required</span>: <span class="token-string">true</span>`)}
    <p>Documentation resources are referenced by <code>docs</code> on a QualityContract and by <code>documentation</code> on a requirement or stage. The document itself remains externally stored and governed by its own access controls.</p>
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
    <div class="callout"><strong>Approval policies reference Role IDs.</strong> The optional <a href="#/team">team list</a> maps people to those roles. The evaluator still reads approved Role IDs from the runtime snapshot; listing a person in the team does not record an approval.</div>
    <p>Version 0.1 does not define ordered approvals, delegation, separation of duties, expiry, or waivers.</p>
  `);
}

function renderTeam() {
  return pageFrame(pages["/team"], `
    <h2>Create a role</h2>
    <p>A <code>Role</code> describes an accountable function. Create it interactively with <code>oq add role</code>; the command writes <code>roles/&lt;id&gt;.yaml</code>. Assign it to a person in that person's <code>team[].roles</code> list.</p>
    ${code(`oq add role`)}
    ${code(`kind: Role
metadata:
  id: software-engineer
  name: Software Engineer
spec:
  description: Implements and reviews software changes.
  responsibilities:
    - Maintain automated tests.
    - Review implementation changes.`)}
    <h2>Example roles</h2>
    <p>The minimal contract also defines roles for engineering and quality responsibilities. Their IDs are assigned to people in the contract's <code>team</code>.</p>
    ${code(`kind: Role
metadata:
  id: tech-lead
  name: Tech Lead
spec:
  responsibilities:
    - Guide technical design and implementation.
    - Coordinate engineering decisions and review technical risks.`)}
    ${code(`kind: Role
metadata:
  id: product-manager
  name: Product Manager
spec:
  responsibilities:
    - Define product goals and prioritize requirements.
    - Clarify business needs and acceptance criteria with stakeholders.`)}
    <h2>Add people to the team</h2>
    ${code(`oq add team`)}
    <p>Enter an email, select existing roles by number or ID separated by commas, and choose whether to add another person. Existing members remain in the contract.</p>
    <p>You can also edit <code>quality-contract.yaml</code> directly. Put <code>team</code> at the root:</p>
    ${code(`team:
  - email: engineer@example.com
    roles:
      - software-engineer
  - email: lead@example.com
    roles:
      - quality-lead
      - engineering-manager`)}
    <h2>Validation rules</h2>
    <ul>
      <li>Each member requires an email and at least one role.</li>
      <li>Each role references the metadata.id of an existing Role resource.</li>
      <li>Emails are unique ignoring case; a member's roles cannot repeat.</li>
      <li>Multiple people can share a role, and each person can have several roles.</li>
      <li>Omitting team or declaring team: [] is valid.</li>
    </ul>
    ${code(`oq validate .quality`)}
    <p>JSON Schema checks the structure and role ID syntax. The CLI also checks duplicate emails and unresolved role references across resources.</p>
    <div class="callout"><strong>Contract roles and provider permissions.</strong> Team assignments describe accountability. They do not automatically invite people to GitHub, GitLab, Jira, or OpenProject, grant permissions, or satisfy approval policies. Provider memberships use their own configuration.</div>
  `);
}

function renderProviders() {
  return pageFrame(pages["/providers"], `
    <p>The Quality Contract stays provider-neutral. Provider configuration lives alongside a <code>QualityContract</code> and is selected by a provider role.</p>
    ${code(`<span class="token-key">workManagement</span>:
  <span class="token-key">provider</span>: <span class="token-string">github</span>
  <span class="token-key">config</span>:
    <span class="token-key">owner</span>: <span class="token-string">your-github-login</span>
    <span class="token-key">ownerType</span>: <span class="token-string">user</span>
    <span class="token-key">project</span>: <span class="token-string">Payment API Quality</span>
<span class="token-key">sourceControl</span>:
  <span class="token-key">provider</span>: <span class="token-string">github</span>
  <span class="token-key">config</span>:
    <span class="token-key">owner</span>: <span class="token-string">your-github-login</span>
    <span class="token-key">ownerType</span>: <span class="token-string">user</span>
    <span class="token-key">repository</span>: <span class="token-string">payment-api</span>
    <span class="token-key">visibility</span>: <span class="token-string">private</span>`)}
    <h2>Two provider roles</h2>
    <p>Choose providers by the work they manage. <code>workManagement</code> connects the contract to a project or board for managing work. <code>sourceControl</code> connects it to the repository where the code lives. Configure either role on its own, or combine both in the same contract.</p>
    <table class="resource-table">
      <thead><tr><th>Role in the contract</th><th>Purpose</th><th>Supported providers</th></tr></thead>
      <tbody>
        <tr><td>workManagement</td><td>Manage projects, workflow boards, columns, and supported work items and memberships.</td><td>OpenProject, GitHub Projects, Jira Cloud</td></tr>
        <tr><td>sourceControl</td><td>Manage code repository access and supported repository provisioning.</td><td>GitHub repositories, GitLab</td></tr>
      </tbody>
    </table>
    <h2>Plan before apply</h2>
    ${code(`oq plan \\
  --target examples/minimal/quality-contract.yaml \\
  --provider-role workManagement \\
  examples/minimal`)}
    <p>Credentials are never declared in provider YAML. They are read from environment variables by the selected adapter.</p>
    ${code(`oq plan
oq apply --provider-role workManagement .quality
oq apply --provider-role sourceControl .quality`)}
    <p>Without a provider-role selector, <code>oq plan</code> and <code>oq apply</code> process every configured role in YAML order.</p>
    <h2 id="work-management">Work management providers</h2>
    <p>These integrations organize the work described by the Quality Contract in an external project or board. Configure OpenProject, GitHub Projects, or Jira Cloud under the root-level <code>workManagement</code> role. Each adapter provisions the resources described below.</p>
    <h3>OpenProject</h3>
    <p>OpenProject is a work-management destination for the contract. The adapter uses the QualityContract's <code>metadata.id</code> as the project identifier and <code>metadata.name</code> as its display name. You can select OpenProject during <code>oq init</code> or configure it directly:</p>
    ${code(`workManagement:
  provider: openproject
  config:
    baseURL: https://openproject.example.com
    members:
      - role: software-engineer
        emails: [engineer@example.com]
        openProjectRole: Member`)}
    <h4>What apply does</h4>
    <ul>
      <li>Creates or updates the project representing the QualityContract.</li>
      <li>Creates or updates a Basic board named after the contract.</li>
      <li>Uses workflow stage IDs as column names in workflow order, such as plan, dev, and rev.</li>
      <li>Adds the configured people to the project with the requested OpenProject roles.</li>
    </ul>
    <p>Stages describe the board's columns; the adapter does not create stage work packages or cards. Board order is a visual arrangement, while execution dependencies remain defined by <code>Stage.spec.dependsOn</code>.</p>
    <h4>Settings and access</h4>
    <table class="resource-table">
      <thead><tr><th>Setting</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>baseURL</td><td>Required instance URL, for example https://openproject.example.com. Use the instance root, not an /api/v3 URL.</td></tr>
        <tr><td>members</td><td>Optional mappings from a contract role to emails and an OpenProject role name.</td></tr>
        <tr><td>kanban.columns</td><td>Optional custom column names; otherwise columns use workflow stage IDs.</td></tr>
        <tr><td>workPackageTypeHref</td><td>Optional preferred type href, such as /api/v3/types/1. The adapter selects an available project type if needed.</td></tr>
      </tbody>
    </table>
    <p>Set <code>OPENPROJECT_TOKEN</code> in the environment before applying. The token's account needs access to manage the project, board, and memberships. If a configured email has no OpenProject account, the adapter invites that person; this requires an administrator token. <code>openProjectRole</code> must name an available role on the instance.</p>
    ${code(`oq plan --provider-role workManagement .quality
oq apply --provider-role workManagement .quality`)}
    <h3>GitHub Projects</h3>
    <p>Use <code>provider: github</code> with <code>config.project</code> for work management. The adapter creates or reuses the project, ensures an <code>Open Quality Stage</code> single-select field with workflow stage IDs as options, and creates an <code>Open Quality workflow</code> Board view grouped by that field. Existing Board views are recognized on later applies. It creates no draft issues or project items.</p>
    <p><code>ownerType</code> defaults to <code>organization</code>; use <code>user</code> for a personal project. The adapter uses GraphQL for projects and fields and REST for view creation. A personal project's view endpoint requires a compatible token; see the <a href="https://docs.github.com/en/rest/projects/views#create-a-view-for-a-user-owned-project" target="_blank" rel="noreferrer">GitHub view API documentation</a> for supported token types.</p>
    ${code(`workManagement:
  provider: github
  config:
    owner: your-github-login
    ownerType: user
    project: Payment API Quality`)}
    <h4>Settings and access</h4>
    <table class="resource-table">
      <thead><tr><th>Setting</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>owner</td><td>Required GitHub login or organization name that owns the project.</td></tr>
        <tr><td>ownerType</td><td>user for a personal project; organization for an organization-owned project. The default is organization.</td></tr>
        <tr><td>project</td><td>Required project title. The adapter searches for an existing project with this title or creates one.</td></tr>
      </tbody>
    </table>
    <p>Set <code>GITHUB_TOKEN</code> with access to read the owner and manage Projects v2, fields, and views. For organization projects, the authenticated account must have access to that organization. The saved project ID and number allow later applies to reuse the same project.</p>
    <h4>What you see in GitHub</h4>
    <p>For a workflow with <code>stages: [plan, dev, rev]</code>, the <code>Open Quality Stage</code> field has three options and the <code>Open Quality workflow</code> Board view uses them as columns. The board starts without cards because this adapter only provisions the project, field, and view. It does not synchronize team members or create a GitHub repository.</p>
    ${code(`oq plan --provider-role workManagement .quality
oq apply --provider-role workManagement .quality`)}
    <p>Although the plan prints <code>Provider: github-projects</code>, the YAML adapter key is <code>provider: github</code>. <code>config.project</code> selects GitHub Projects; <code>config.repository</code> selects the separate source-control adapter.</p>
    <h3>Jira Cloud</h3>
    <p>Jira Cloud represents the contract as a Jira project and its quality requirements as issues. Select Jira Cloud during <code>oq init</code>, then provide the instance URL and a project key:</p>
    ${code(`workManagement:
  provider: jira-cloud
  config:
    baseURL: https://your-domain.atlassian.net
    projectKey: PAY
    issueTypeName: Task
    members:
      - role: software-engineer
        emails: [engineer@example.com]
        jiraProjectRole: Developers`)}
    <h4>What apply does</h4>
    <ul>
      <li>Creates or reuses the project identified by projectKey, using the contract's name for a new project.</li>
      <li>Creates or reuses a Kanban board named after the contract and configures its columns.</li>
      <li>Resolves or invites the configured people and adds them to their Jira project roles.</li>
      <li>Creates issues for declared quality requirements using the configured issue type.</li>
    </ul>
    <p>Workflow stages become column names rather than Jira issues. A contract with <code>quality.characteristics: []</code> has no requirement issues to create. Columns default to workflow stage IDs in list order; <code>config.kanban.columns</code> can override their display names.</p>
    <h4>Settings and access</h4>
    <table class="resource-table">
      <thead><tr><th>Setting</th><th>Meaning</th></tr></thead>
      <tbody>
        <tr><td>baseURL</td><td>Required Jira Cloud instance root, such as https://your-domain.atlassian.net.</td></tr>
        <tr><td>projectKey</td><td>Required key such as PAY or PAY7. At least two characters, starting with an uppercase ASCII letter, followed only by uppercase ASCII letters or digits.</td></tr>
        <tr><td>issueTypeName</td><td>Issue type for requirement issues; defaults to Task and must exist in the target project.</td></tr>
        <tr><td>projectTemplateKey</td><td>Optional project-creation template; defaults to com.pyxis.greenhopper.jira:gh-kanban-template.</td></tr>
        <tr><td>members</td><td>Optional contract role, emails, and jiraProjectRole mappings. The Jira role must exist in the project.</td></tr>
      </tbody>
    </table>
    <p>Set both <code>JIRA_EMAIL</code> and <code>JIRA_API_TOKEN</code> for the account used by the adapter. That account needs permission to perform the configured operations, including project or board creation, issue creation, membership changes, and invitations when needed.</p>
    <p>The current adapter renames board columns through Jira's internal board-settings endpoint. When the requested column count differs, it redistributes existing statuses while preserving their order and keeping completed statuses in the final column. The rightmost column represents completed work; review the board's status mapping after applying a changed workflow.</p>
    ${code(`oq plan --provider-role workManagement .quality
oq apply --provider-role workManagement .quality`)}
    <h2 id="source-control">Code management providers</h2>
    <p>These integrations manage the repository that stores your code and the people who can access it. Configure GitHub or GitLab under the root-level <code>sourceControl</code> role. For example, use Jira Cloud for work management and GitHub for source control; the choices are independent.</p>
    <h3>GitHub repositories</h3>
    <p>Use <code>provider: github</code> with <code>config.repository</code> for source control. The adapter ensures the repository exists and applies configured collaborator permissions. It does not create CI/CD workflows or repository rulesets.</p>
    <div class="callout"><strong>Choose the correct owner.</strong> For a personal repository, owner is the GitHub login authenticated by GITHUB_TOKEN, not the project or repository name. To create your-github-login/payment-api, use owner: your-github-login and repository: payment-api. For organization-owned resources, use ownerType: organization and an account with the required access.</div>
    ${code(`sourceControl:
  provider: github
  config:
    owner: your-github-login
    ownerType: user
    repository: payment-api
    visibility: private
    members:
      - role: software-engineer
        usernames: [collaborator-login]
        permission: push`)}
    <p><code>visibility</code> defaults to <code>private</code>. Members use GitHub usernames and a repository permission, such as <code>push</code>. The token must permit the requested repository and collaborator operations.</p>
    <h3>GitLab</h3>
    <p>The GitLab adapter adds configured members to an existing project. It uses GitLab usernames and an access level, such as <code>developer</code>. Set <code>GITLAB_TOKEN</code> with permission to manage memberships in that project.</p>
    ${code(`sourceControl:
  provider: gitlab
  config:
    baseURL: https://gitlab.com/api/v4
    project: your-group/payment-api
    members:
      - role: software-engineer
        usernames: [collaborator-login]
        accessLevel: developer`)}
    <p>The adapter leaves the project's CI/CD configuration and merge policies unchanged.</p>
    ${code(`oq plan --provider-role sourceControl .quality
oq apply --provider-role sourceControl .quality`)}
    <h2>Contract team and provider memberships</h2>
    <p><code>team</code> assigns people to contract Role IDs. Provider memberships are configured separately under <code>config.members</code>: OpenProject uses <code>openProjectRole</code>, and Jira uses <code>jiraProjectRole</code>. These are role names in the external system, not contract Role IDs. GitHub Projects currently does not provision memberships from either <code>team</code> or <code>config.members</code>.</p>
    <p>You can choose one work-management provider and combine it with GitHub or GitLab source control. Replace the <code>workManagement</code> example with the adapter you use; run <code>oq init</code> to generate its base configuration.</p>
    <h2>Credentials and local state</h2>
    <table class="resource-table">
      <thead><tr><th>Adapter</th><th>Environment variables</th></tr></thead>
      <tbody>
        <tr><td>GitHub Projects / repositories</td><td>GITHUB_TOKEN</td></tr>
        <tr><td>GitLab</td><td>GITLAB_TOKEN</td></tr>
        <tr><td>OpenProject</td><td>OPENPROJECT_TOKEN</td></tr>
        <tr><td>Jira Cloud</td><td>JIRA_EMAIL and JIRA_API_TOKEN</td></tr>
      </tbody>
    </table>
    <p>GitHub Projects saves the project ID and number in a role-specific local file such as <code>.quality/quality-contract.yaml.workManagement.state.json</code>. Keep that file to reuse the project after a partial apply. If view creation fails, the error includes its REST route; check the owner, project number, and token access, then rerun the selected role.</p>
  `);
}

function renderVersioning() {
  return pageFrame(pages["/versioning"], `
    <h2>Schema selection</h2>
    <p>Resource documents do not carry a version field. The CLI release determines which schema validates them.</p>
    <h2>Contract history</h2>
    <p>Track contract evolution in source control.</p>
    <h2>Before 1.0</h2>
    <p>Breaking format changes may require updating existing contracts. Release notes describe these changes.</p>
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
    const content = `${page.title} ${page.description} ${page.keywords || ""} ${path}`.toLowerCase();
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
