# Quality as Code Manifesto

Software engineering has made infrastructure, delivery pipelines, configuration, and policy explicit and versionable. Software quality, however, is still commonly fragmented across documents, dashboards, test tools, ticket systems, informal approvals, and team knowledge.

This fragmentation makes a basic question surprisingly difficult to answer:

> What does quality mean for this system, and what evidence proves that the expectation is being met?

**Quality as Code** is the practice of representing quality expectations and the process used to verify them as declarative artifacts that live with the software.

We value:

- explicit quality expectations over implicit assumptions;
- measurable criteria over subjective status labels;
- traceable evidence over unsupported confidence;
- versioned decisions over undocumented process;
- open, portable contracts over vendor-specific configuration;
- automation where appropriate and accountable human judgment where necessary;
- visible, time-bound exceptions over silent bypasses.

These values do not imply that every aspect of quality can be reduced to a number or automatically enforced. They mean that expectations, responsibilities, evidence, and decisions should be clear enough to inspect, review, and evolve.

Open Quality provides a concrete specification for expressing this practice. Any tool may implement it; no single platform owns the methodology.
