export const meta = {
  name: 'workshop-problem-engine',
  description: 'Engine for phases 2–6 of the workshop-problem lifecycle: ground in prior art, implement, adversarially red-team, converge until green on the charter, then review. Phases 0–1 (scope + charter) happen in conversation BEFORE this runs; the agreed charter is the input contract and the loop oracle.',
  phases: [
    { title: 'Ground', detail: 'inventory existing machinery; early-exit on blockers' },
    { title: 'Implement', detail: 'attempt the solution against charter + ledger' },
    { title: 'Red-team', detail: 'adversarial panel attacks the attempt vs charter §2' },
    { title: 'Converge', detail: 'fix findings; loop until green or cap' },
    { title: 'Review', detail: 'final adversarial / PR-style review' },
  ],
}

// ---- input contract -------------------------------------------------------
// args = {
//   charter:       string  (REQUIRED — full text of the agreed charter; §2 is the oracle)
//   ledgerPath?:   string  (where to write/read the prior-art ledger; code-in-a-repo only)
//   maxIterations?:number  (hard cap on the implement↔red-team loop; default 3)
// }
const charter = args && args.charter
const ledgerPath = (args && args.ledgerPath) || '.coder/ledger.md'
const MAX_ITERS = (args && args.maxIterations) || 3

if (!charter || typeof charter !== 'string') {
  // No charter => phases 0–1 were skipped. Refuse rather than guess the question.
  return { status: 'no-charter', message: 'workshop-problem engine requires an agreed charter (phases 0–1) as args.charter.' }
}

// ---- schemas --------------------------------------------------------------
const GROUND = {
  type: 'object', additionalProperties: false,
  properties: {
    summary: { type: 'string', description: 'what already exists that bears on this problem' },
    machinery: { type: 'array', items: { type: 'string' }, description: 'existing tested symbols/modules to reuse or extend (path:line)' },
    reusePlan: { type: 'array', items: { type: 'string' }, description: 'per quantity: reuse / extend / new + one-line reason' },
    blockers: {
      type: 'array',
      description: 'blocking unknowns or signs the charter is mis-scoped; non-empty => engine must stop and return to the human',
      items: {
        type: 'object', additionalProperties: false,
        properties: { question: { type: 'string' }, blocks: { type: 'string' } },
        required: ['question', 'blocks'],
      },
    },
  },
  required: ['summary', 'machinery', 'reusePlan', 'blockers'],
}

const IMPLEMENT = {
  type: 'object', additionalProperties: false,
  properties: {
    summary: { type: 'string' },
    changes: { type: 'array', items: { type: 'string' }, description: 'files/symbols added or changed' },
    tests: { type: 'array', items: { type: 'string' }, description: 'tests added/run and their result' },
    openItems: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'changes'],
}

const REDTEAM = {
  type: 'object', additionalProperties: false,
  properties: {
    lens: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          criterion: { type: 'string', description: 'which charter §2 criterion (or invariant) is at risk' },
          problem: { type: 'string' },
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          real: { type: 'boolean', description: 'true only if you can substantiate it; default false when unsure' },
        },
        required: ['criterion', 'problem', 'severity', 'real'],
      },
    },
    verdict: { type: 'string', enum: ['breaks', 'holds', 'unsure'] },
  },
  required: ['lens', 'findings', 'verdict'],
}

const REVIEW = {
  type: 'object', additionalProperties: false,
  properties: {
    verdict: { type: 'string', enum: ['approve', 'approve-with-nits', 'reject'] },
    mustFix: { type: 'array', items: { type: 'string' } },
    residualRisks: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['verdict', 'mustFix', 'residualRisks', 'summary'],
}

const CHARTER_BLOCK = `--- CHARTER (the contract; §2 is the definition-of-done you are judged against) ---\n${charter}\n--- END CHARTER ---`

// ---- Phase 2: Ground ------------------------------------------------------
phase('Ground')
const ground = await agent(
  `${CHARTER_BLOCK}\n\nApply the prior-art-ledger discipline to THIS problem. Read-only except the ledger file (${ledgerPath}). Inventory the existing, tested machinery, the local definitions/conventions, and the invariants that bear on the charter. Decide reuse / extend / new for each quantity the task needs. Then judge the framing: if a load-bearing unknown remains, or the charter looks mis-scoped or self-contradictory, record it as a BLOCKER — do NOT paper over it. Return the structured result; write or refresh the ledger at ${ledgerPath}.`,
  { phase: 'Ground', label: 'ground', schema: GROUND },
)

if (!ground) return { status: 'error', phase: 'Ground', message: 'grounding agent failed' }
if (ground.blockers && ground.blockers.length) {
  log(`Ground surfaced ${ground.blockers.length} blocker(s) — returning to the human rather than guessing.`)
  return { status: 'blocked', blockers: ground.blockers, ground }
}
const GROUND_BLOCK = `--- GROUNDING (prior art; honor reuse plan, definitions, invariants) ---\nsummary: ${ground.summary}\nmachinery: ${ground.machinery.join('; ')}\nreusePlan: ${ground.reusePlan.join('; ')}\n--- END GROUNDING ---`

// ---- Phase 3: Implement ---------------------------------------------------
phase('Implement')
let impl = await agent(
  `${CHARTER_BLOCK}\n\n${GROUND_BLOCK}\n\nImplement the solution. Prefer reuse/extend over new per the grounding. Honor every definition and invariant. Add tests (delegate in spirit to test-generator) for new behavior and run them. Aim squarely at making every charter §2 criterion true. Return what you changed.`,
  { phase: 'Implement', label: 'implement', schema: IMPLEMENT },
)
if (!impl) return { status: 'error', phase: 'Implement', message: 'implementation agent failed', ground }

// ---- Phases 4–5: Red-team ↔ Converge loop ---------------------------------
const LENSES = [
  { key: 'criteria', focus: 'Go criterion by criterion through charter §2. For each, try to show it does NOT yet hold. A criterion you cannot decide is itself a finding.' },
  { key: 'invariants', focus: 'Attack the assumptions and invariants from the grounding. Find an input or state that violates one and breaks the result.' },
  { key: 'edges', focus: 'Hunt edge cases, boundary conditions, and failure modes the implementation glosses over.' },
]

let green = false
let iters = 0
let lastFindings = []

while (iters < MAX_ITERS) {
  iters++
  // Budget guard: stop spending if the turn's token target is nearly exhausted.
  if (budget.total && budget.remaining() < 60_000) {
    log(`Stopping converge loop early at iteration ${iters}: token budget nearly exhausted.`)
    break
  }

  phase('Red-team')
  const implBlock = `--- CURRENT ATTEMPT (iteration ${iters}) ---\nsummary: ${impl.summary}\nchanges: ${impl.changes.join('; ')}\ntests: ${(impl.tests || []).join('; ')}\nopen: ${(impl.openItems || []).join('; ')}\n--- END ATTEMPT ---`
  const panel = await parallel(LENSES.map((lens) => () =>
    agent(
      `${CHARTER_BLOCK}\n\n${implBlock}\n\nYou are an adversarial reviewer. Lens: ${lens.focus} Be skeptical; mark a finding real:true ONLY if you can substantiate it, and default real:false when unsure. Verdict 'breaks' if any real high/medium finding stands.`,
      { phase: 'Red-team', label: `redteam:${lens.key}`, schema: REDTEAM },
    )))

  const surviving = panel.filter(Boolean)
    .flatMap((p) => p.findings)
    .filter((f) => f.real && (f.severity === 'high' || f.severity === 'medium'))
  lastFindings = surviving

  if (surviving.length === 0) {
    green = true
    log(`Iteration ${iters}: red-team found no surviving high/medium findings — green on charter.`)
    break
  }
  log(`Iteration ${iters}: ${surviving.length} surviving finding(s); feeding back to implementation.`)

  if (iters >= MAX_ITERS) break // hit cap with findings still open

  phase('Converge')
  const findingsBlock = surviving.map((f, i) => `${i + 1}. [${f.severity}] (${f.criterion}) ${f.problem}`).join('\n')
  impl = await agent(
    `${CHARTER_BLOCK}\n\n${GROUND_BLOCK}\n\n--- PRIOR ATTEMPT ---\n${impl.summary}\nchanges: ${impl.changes.join('; ')}\n--- RED-TEAM FINDINGS TO FIX ---\n${findingsBlock}\n\nRevise the implementation to resolve every finding above without violating the charter or the grounding. Re-run tests. Return the updated state.`,
    { phase: 'Converge', label: `converge:${iters}`, schema: IMPLEMENT },
  )
  if (!impl) return { status: 'error', phase: 'Converge', message: 'fix agent failed', ground, iterations: iters }
}

// ---- Phase 6: Review ------------------------------------------------------
phase('Review')
const review = await agent(
  `${CHARTER_BLOCK}\n\n--- FINAL ATTEMPT ---\nsummary: ${impl.summary}\nchanges: ${impl.changes.join('; ')}\ntests: ${(impl.tests || []).join('; ')}\n--- END ---\n\nFinal adversarial review, PR-style (code-reviewer for code, technical-editor for prose). Confirm each charter §2 criterion. List anything that MUST be fixed before sign-off and any residual risks the human should know. Be honest: do not approve if a §2 criterion is unmet.`,
  { phase: 'Review', label: 'review', schema: REVIEW },
)

return {
  status: green ? 'green' : 'not-converged',
  green,
  iterations: iters,
  openFindings: green ? [] : lastFindings,
  ground,
  implementation: impl,
  review,
  note: green
    ? 'Met the charter definition-of-done; see review for residual risks. Human sign-off still required.'
    : `Did NOT reach green within ${MAX_ITERS} iteration(s). Open findings listed; return to the human — do not treat as done.`,
}
