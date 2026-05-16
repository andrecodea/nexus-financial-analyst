# CopilotKit Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the Thesys-first GenUI plan with an open-source CopilotKit + AG-UI architecture for Nexus Financial Analyst.

**Architecture:** LangGraph or DeepAgents owns agent reasoning, RAG, tool calls, memory, and workflow state. CopilotKit owns the React agent UI, shared state, human-in-the-loop interactions, and generative UI rendering through structured events/components. Financial data tools stay behind typed backend contracts so the UI can render evidence, hypotheses, simulations, and thesis state without depending on a proprietary GenUI model.

**Tech Stack:** FastAPI, Python, LangGraph/DeepAgents, CopilotKit, AG-UI, React, Vite, TypeScript, Pydantic, yfinance, Tavily, SEC/filings APIs, optional vector store.

---

## Source Notes

- CopilotKit is open-source under the MIT license in the public GitHub repository: https://github.com/CopilotKit/CopilotKit
- CopilotKit positions itself as a frontend stack for agents and generative UI with React/Angular support: https://docs.showcase.copilotkit.ai/
- The LangChain docs describe a CopilotKit + LangGraph pattern where a custom endpoint connects a React runtime to a LangGraph deployment and renders structured UI payloads: https://docs.langchain.com/oss/javascript/langchain/frontend/integrations/copilotkit
- AG-UI is an open, event-based protocol for connecting agents to user-facing applications: https://docs.ag-ui.com/

## Current Project Facts

- `frontend/index.html` points to `/src/main.tsx`, but `frontend/src` is missing.
- `frontend/package.json` includes `@thesysai/genui-sdk` and `@crayonai/react-ui`, but there is no source code using them.
- `backend/main.py` streams plain model text from LangChain events.
- `backend/prompt.toml` duplicates the large system prompt embedded in `backend/main.py`.
- `backend/tools.py` returns raw `yfinance` and Tavily data without stable Pydantic response contracts.
- The Git repo has no commits yet and many untracked generated/runtime files.

## Target Product Direction

Pivot the product from a generic financial chat dashboard to **Nexus Thesis OS**:

- Build and update investment or business theses.
- Extract claims from documents, reports, filings, news, and user notes.
- Retrieve evidence for and against each claim.
- Maintain competing hypotheses.
- Render simulations, evidence boards, timelines, and risk matrices.
- Let the user approve, reject, edit, or escalate agent-generated findings.

## File Structure

Create or modify these areas:

- Create `docs/architecture/copilotkit-agui.md` to document the long-term architecture and event contracts.
- Create `backend/app/` as the new backend package.
- Create `backend/app/main.py` for FastAPI app wiring.
- Create `backend/app/agents/graph.py` for LangGraph/DeepAgents orchestration.
- Create `backend/app/agents/state.py` for agent state models.
- Create `backend/app/tools/market_data.py` for price and historical data.
- Create `backend/app/tools/news.py` for news/web search.
- Create `backend/app/tools/filings.py` for SEC/filing retrieval.
- Create `backend/app/schemas/financial.py` for typed financial tool outputs.
- Create `backend/app/schemas/thesis.py` for thesis, claim, evidence, scenario, and risk models.
- Create `backend/app/api/copilotkit.py` for the CopilotKit/AG-UI runtime endpoint.
- Create `frontend/src/main.tsx` for React bootstrapping.
- Create `frontend/src/App.tsx` for CopilotKit provider and app layout.
- Create `frontend/src/components/copilot/FinancialCopilot.tsx` for chat/runtime UI.
- Create `frontend/src/components/genui/` for custom generated UI components.
- Create `frontend/src/lib/copilotkit.ts` for runtime URL and component registry configuration.
- Create tests under `backend/tests/` and `frontend/src/**/*.test.tsx`.

## Task 1: Repository Hygiene

**Files:**
- Modify: `.gitignore`
- Create: `README.md`
- Create: `.env.example`

- [ ] **Step 1: Add root ignore rules**

Use the root `.gitignore` to exclude secrets, virtual environments, build outputs, IDE files, and generated frontend bundles:

```gitignore
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
.venv/
venv/
node_modules/
frontend/dist/
frontend/dist-ssr/
.idea/
.vscode/*
!.vscode/extensions.json
.DS_Store
```

- [ ] **Step 2: Create environment example**

Create `.env.example`:

```dotenv
OPENAI_API_KEY=
TAVILY_API_KEY=
APP_ENV=development
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8888
FRONTEND_PORT=3000
```

- [ ] **Step 3: Create root README**

Create `README.md`:

```markdown
# Nexus Financial Analyst

Nexus Financial Analyst is an agent-native financial research workspace. The target architecture uses LangGraph or DeepAgents for reasoning and RAG, CopilotKit for the open-source frontend agent runtime, and AG-UI-compatible structured events for generative UI.

## Local Development

Backend:

```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8888
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```
```

- [ ] **Step 4: Verify Git only sees intended source files**

Run:

```powershell
git status --short
```

Expected: `.env`, `.venv`, `frontend/dist`, and `.idea` are not listed after ignore rules are applied.

## Task 2: Backend Package Foundation

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/settings.py`
- Modify: `backend/pyproject.toml`
- Test: `backend/tests/test_settings.py`

- [ ] **Step 1: Add settings test**

Create `backend/tests/test_settings.py`:

```python
from backend.app.settings import Settings


def test_settings_defaults_for_local_development():
    settings = Settings(openai_api_key="test", tavily_api_key="test")

    assert settings.app_env == "development"
    assert settings.backend_port == 8888
    assert settings.copilotkit_route == "/api/copilotkit"
```

- [ ] **Step 2: Implement settings**

Create `backend/app/settings.py`:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str = Field(min_length=1)
    tavily_api_key: str = Field(min_length=1)
    app_env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8888
    copilotkit_route: str = "/api/copilotkit"
```

- [ ] **Step 3: Add backend dependencies**

Modify `backend/pyproject.toml` dependencies:

```toml
dependencies = [
    "fastapi>=0.127.0",
    "langchain[openai]>=1.2.0",
    "langgraph>=1.0.5",
    "pydantic>=2.12.5",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.2.1",
    "tavily-python>=0.7.17",
    "uvicorn>=0.40.0",
    "yfinance>=1.0",
]
```

- [ ] **Step 4: Create FastAPI app factory**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.copilotkit import router as copilotkit_router


def create_app() -> FastAPI:
    app = FastAPI(title="Nexus Thesis OS")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(copilotkit_router)
    return app


app = create_app()
```

- [ ] **Step 5: Run backend test**

Run:

```powershell
cd backend
uv run pytest tests/test_settings.py -q
```

Expected: one passing test.

## Task 3: Typed Financial Data Contracts

**Files:**
- Create: `backend/app/schemas/financial.py`
- Create: `backend/app/tools/market_data.py`
- Test: `backend/tests/test_market_data_schema.py`

- [ ] **Step 1: Write schema test**

Create `backend/tests/test_market_data_schema.py`:

```python
from datetime import datetime, timezone

from backend.app.schemas.financial import PriceSnapshot


def test_price_snapshot_serializes_for_genui():
    snapshot = PriceSnapshot(
        ticker="AAPL",
        price=190.25,
        currency="USD",
        source="yfinance",
        observed_at=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )

    payload = snapshot.model_dump(mode="json")

    assert payload["ticker"] == "AAPL"
    assert payload["price"] == 190.25
    assert payload["source"] == "yfinance"
    assert payload["observed_at"] == "2026-05-16T00:00:00Z"
```

- [ ] **Step 2: Implement financial schema**

Create `backend/app/schemas/financial.py`:

```python
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class PriceSnapshot(BaseModel):
    ticker: str = Field(min_length=1)
    price: float
    currency: str = "USD"
    source: Literal["yfinance", "polygon", "finnhub", "manual"]
    observed_at: datetime


class PricePoint(BaseModel):
    ticker: str
    date: str
    close: float
    volume: int | None = None


class NewsItem(BaseModel):
    title: str
    url: str
    publisher: str | None = None
    published_at: datetime | None = None
    summary: str | None = None
```

- [ ] **Step 3: Implement market data wrapper**

Create `backend/app/tools/market_data.py`:

```python
from datetime import datetime, timezone

import yfinance as yf

from backend.app.schemas.financial import PriceSnapshot


def get_price_snapshot(ticker: str) -> PriceSnapshot:
    normalized_ticker = ticker.strip().upper()
    stock = yf.Ticker(normalized_ticker)
    history = stock.history(period="1d")
    if history.empty:
        raise ValueError(f"No price data returned for ticker {normalized_ticker}")

    return PriceSnapshot(
        ticker=normalized_ticker,
        price=float(history["Close"].iloc[-1]),
        currency=stock.fast_info.get("currency", "USD"),
        source="yfinance",
        observed_at=datetime.now(timezone.utc),
    )
```

- [ ] **Step 4: Run schema test**

Run:

```powershell
cd backend
uv run pytest tests/test_market_data_schema.py -q
```

Expected: one passing test.

## Task 4: Thesis RAG Domain Models

**Files:**
- Create: `backend/app/schemas/thesis.py`
- Test: `backend/tests/test_thesis_schema.py`

- [ ] **Step 1: Write thesis schema test**

Create `backend/tests/test_thesis_schema.py`:

```python
from backend.app.schemas.thesis import Claim, Evidence, Thesis


def test_thesis_tracks_claims_and_evidence():
    evidence = Evidence(
        source_id="sec-aapl-10k-2025",
        title="Apple 2025 10-K",
        url="https://www.sec.gov/",
        excerpt="Revenue increased year over year.",
        stance="supports",
        confidence=0.72,
    )
    claim = Claim(
        id="claim-1",
        text="Apple has resilient revenue growth.",
        status="needs_review",
        evidence=[evidence],
    )
    thesis = Thesis(
        id="thesis-1",
        title="AAPL 18-month investment thesis",
        summary="A structured thesis with auditable evidence.",
        claims=[claim],
    )

    assert thesis.claims[0].evidence[0].stance == "supports"
```

- [ ] **Step 2: Implement thesis schema**

Create `backend/app/schemas/thesis.py`:

```python
from typing import Literal

from pydantic import BaseModel, Field


EvidenceStance = Literal["supports", "contradicts", "context", "unclear"]
ClaimStatus = Literal["draft", "needs_review", "accepted", "rejected"]


class Evidence(BaseModel):
    source_id: str
    title: str
    url: str | None = None
    excerpt: str
    stance: EvidenceStance
    confidence: float = Field(ge=0, le=1)


class Claim(BaseModel):
    id: str
    text: str
    status: ClaimStatus = "draft"
    evidence: list[Evidence] = Field(default_factory=list)


class ScenarioInput(BaseModel):
    name: str
    value: float
    unit: str


class Scenario(BaseModel):
    id: str
    title: str
    inputs: list[ScenarioInput]
    interpretation: str


class Thesis(BaseModel):
    id: str
    title: str
    summary: str
    claims: list[Claim] = Field(default_factory=list)
    scenarios: list[Scenario] = Field(default_factory=list)
```

- [ ] **Step 3: Run thesis schema test**

Run:

```powershell
cd backend
uv run pytest tests/test_thesis_schema.py -q
```

Expected: one passing test.

## Task 5: LangGraph Agent State

**Files:**
- Create: `backend/app/agents/state.py`
- Create: `backend/app/agents/graph.py`
- Test: `backend/tests/test_agent_state.py`

- [ ] **Step 1: Write state test**

Create `backend/tests/test_agent_state.py`:

```python
from backend.app.agents.state import NexusAgentState


def test_agent_state_defaults_to_empty_thesis_workspace():
    state = NexusAgentState(user_message="Compare AMD and NVDA")

    assert state.user_message == "Compare AMD and NVDA"
    assert state.claims == []
    assert state.evidence == []
    assert state.ui_events == []
```

- [ ] **Step 2: Implement state model**

Create `backend/app/agents/state.py`:

```python
from pydantic import BaseModel, Field

from backend.app.schemas.thesis import Claim, Evidence


class NexusAgentState(BaseModel):
    user_message: str
    intent: str | None = None
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    ui_events: list[dict] = Field(default_factory=list)
```

- [ ] **Step 3: Implement initial graph factory**

Create `backend/app/agents/graph.py`:

```python
from langgraph.graph import END, StateGraph

from backend.app.agents.state import NexusAgentState


def classify_intent(state: NexusAgentState) -> NexusAgentState:
    message = state.user_message.lower()
    if "compare" in message or " vs " in message:
        state.intent = "comparison_thesis"
    elif "risk" in message:
        state.intent = "risk_audit"
    else:
        state.intent = "single_thesis"
    return state


def build_graph():
    graph = StateGraph(NexusAgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", END)
    return graph.compile()
```

- [ ] **Step 4: Run state test**

Run:

```powershell
cd backend
uv run pytest tests/test_agent_state.py -q
```

Expected: one passing test.

## Task 6: CopilotKit Runtime Endpoint

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/copilotkit.py`
- Test: `backend/tests/test_copilotkit_endpoint.py`

- [ ] **Step 1: Write endpoint smoke test**

Create `backend/tests/test_copilotkit_endpoint.py`:

```python
from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_copilotkit_health_route():
    client = TestClient(create_app())

    response = client.get("/api/copilotkit/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "runtime": "copilotkit"}
```

- [ ] **Step 2: Implement router**

Create `backend/app/api/copilotkit.py`:

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/copilotkit", tags=["copilotkit"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "runtime": "copilotkit"}
```

- [ ] **Step 3: Add AG-UI event contract document**

Create `docs/architecture/copilotkit-agui.md`:

```markdown
# CopilotKit + AG-UI Architecture

The backend emits agent interaction events. The frontend consumes those events through CopilotKit and renders either chat messages or registered generative UI components.

## Core Event Types

- `text_message`: assistant text for chat.
- `state_delta`: update to thesis, claims, evidence, scenarios, or selected tickers.
- `tool_call`: visible tool execution state.
- `component`: request to render a registered React component with typed props.
- `human_review`: request for the user to approve, reject, or edit a claim.

## Component Registry

- `ThesisBoard`
- `EvidenceMatrix`
- `ScenarioSimulator`
- `TickerComparison`
- `RiskRadar`
```

- [ ] **Step 4: Run endpoint test**

Run:

```powershell
cd backend
uv run pytest tests/test_copilotkit_endpoint.py -q
```

Expected: one passing test.

## Task 7: Restore React Source With CopilotKit

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/components/copilot/FinancialCopilot.tsx`
- Create: `frontend/src/styles.css`

- [ ] **Step 1: Replace Thesys packages**

Modify `frontend/package.json` dependencies:

```json
{
  "dependencies": {
    "@copilotkit/react-core": "^1.57.1",
    "@copilotkit/react-ui": "^1.57.1",
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  }
}
```

- [ ] **Step 2: Create React bootstrap**

Create `frontend/src/main.tsx`:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import "@copilotkit/react-ui/styles.css";
import "./styles.css";
import { App } from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

- [ ] **Step 3: Create CopilotKit app shell**

Create `frontend/src/App.tsx`:

```tsx
import { CopilotKit } from "@copilotkit/react-core";
import { FinancialCopilot } from "./components/copilot/FinancialCopilot";

export function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <FinancialCopilot />
    </CopilotKit>
  );
}
```

- [ ] **Step 4: Create first copilot UI**

Create `frontend/src/components/copilot/FinancialCopilot.tsx`:

```tsx
import { CopilotChat } from "@copilotkit/react-ui";

export function FinancialCopilot() {
  return (
    <main className="app-shell">
      <section className="workspace">
        <header className="workspace-header">
          <p>Nexus Thesis OS</p>
          <h1>Build, audit, and update financial theses.</h1>
        </header>
        <CopilotChat
          labels={{
            title: "Research copilot",
            initial: "Ask me to build a thesis, audit claims, or compare companies.",
          }}
        />
      </section>
    </main>
  );
}
```

- [ ] **Step 5: Add base CSS**

Create `frontend/src/styles.css`:

```css
:root {
  color: #17202a;
  background: #f6f8fb;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

body {
  margin: 0;
}

.app-shell {
  min-height: 100vh;
  display: grid;
  place-items: stretch;
}

.workspace {
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 16px;
  padding: 24px;
}

.workspace-header p {
  margin: 0 0 6px;
  color: #52616f;
  font-size: 14px;
}

.workspace-header h1 {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
}
```

- [ ] **Step 6: Run frontend build**

Run:

```powershell
cd frontend
npm install
npm run build
```

Expected: TypeScript and Vite build pass.

## Task 8: Generative UI Component Registry

**Files:**
- Create: `frontend/src/components/genui/ThesisBoard.tsx`
- Create: `frontend/src/components/genui/EvidenceMatrix.tsx`
- Create: `frontend/src/components/genui/ScenarioSimulator.tsx`
- Create: `frontend/src/lib/componentRegistry.ts`

- [ ] **Step 1: Create ThesisBoard**

Create `frontend/src/components/genui/ThesisBoard.tsx`:

```tsx
type Claim = {
  id: string;
  text: string;
  status: "draft" | "needs_review" | "accepted" | "rejected";
};

type ThesisBoardProps = {
  title: string;
  summary: string;
  claims: Claim[];
};

export function ThesisBoard({ title, summary, claims }: ThesisBoardProps) {
  return (
    <section className="genui-panel">
      <h2>{title}</h2>
      <p>{summary}</p>
      <ul>
        {claims.map((claim) => (
          <li key={claim.id}>
            <strong>{claim.status}</strong>
            <span>{claim.text}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

- [ ] **Step 2: Create EvidenceMatrix**

Create `frontend/src/components/genui/EvidenceMatrix.tsx`:

```tsx
type Evidence = {
  source_id: string;
  title: string;
  excerpt: string;
  stance: "supports" | "contradicts" | "context" | "unclear";
  confidence: number;
};

type EvidenceMatrixProps = {
  evidence: Evidence[];
};

export function EvidenceMatrix({ evidence }: EvidenceMatrixProps) {
  return (
    <table className="evidence-matrix">
      <thead>
        <tr>
          <th>Source</th>
          <th>Stance</th>
          <th>Confidence</th>
          <th>Excerpt</th>
        </tr>
      </thead>
      <tbody>
        {evidence.map((item) => (
          <tr key={item.source_id}>
            <td>{item.title}</td>
            <td>{item.stance}</td>
            <td>{Math.round(item.confidence * 100)}%</td>
            <td>{item.excerpt}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

- [ ] **Step 3: Create component registry**

Create `frontend/src/lib/componentRegistry.ts`:

```tsx
import { EvidenceMatrix } from "../components/genui/EvidenceMatrix";
import { ThesisBoard } from "../components/genui/ThesisBoard";

export const componentRegistry = {
  EvidenceMatrix,
  ThesisBoard,
};
```

- [ ] **Step 4: Wire registry into CopilotKit rendering**

Modify the Copilot UI so structured backend events can select a component by name and pass validated props. Keep the rendering constrained to `componentRegistry` keys.

## Task 9: Human-In-The-Loop Review

**Files:**
- Create: `frontend/src/components/genui/ClaimReviewQueue.tsx`
- Modify: `backend/app/schemas/thesis.py`
- Modify: `backend/app/agents/state.py`

- [ ] **Step 1: Add review action schema**

Add to `backend/app/schemas/thesis.py`:

```python
class ClaimReviewAction(BaseModel):
    claim_id: str
    action: Literal["accept", "reject", "edit"]
    edited_text: str | None = None
```

- [ ] **Step 2: Add review queue UI**

Create `frontend/src/components/genui/ClaimReviewQueue.tsx`:

```tsx
type ReviewClaim = {
  id: string;
  text: string;
};

type ClaimReviewQueueProps = {
  claims: ReviewClaim[];
  onReview: (claimId: string, action: "accept" | "reject") => void;
};

export function ClaimReviewQueue({ claims, onReview }: ClaimReviewQueueProps) {
  return (
    <section className="genui-panel">
      <h2>Claims for review</h2>
      {claims.map((claim) => (
        <article key={claim.id}>
          <p>{claim.text}</p>
          <button onClick={() => onReview(claim.id, "accept")}>Accept</button>
          <button onClick={() => onReview(claim.id, "reject")}>Reject</button>
        </article>
      ))}
    </section>
  );
}
```

- [ ] **Step 3: Add backend handling for user review**

The agent state should store review decisions and use them before generating a final thesis summary.

## Task 10: Verification And Migration Cutover

**Files:**
- Modify: `backend/main.py`
- Modify: `frontend/package.json`
- Modify: `frontend/src/App.tsx`
- Test: backend and frontend test suites

- [ ] **Step 1: Remove Thesys dependencies**

Remove from `frontend/package.json`:

```json
"@thesysai/genui-sdk": "^0.7.11",
"@crayonai/react-ui": "^0.9.8"
```

- [ ] **Step 2: Keep a rollback note**

Add to `docs/architecture/copilotkit-agui.md`:

```markdown
## Rollback

The old Thesys experiment can be recovered from Git history if needed. The core product direction is CopilotKit + AG-UI because it is open-source, app-controlled, and better aligned with custom RAG workspaces.
```

- [ ] **Step 3: Run full backend verification**

Run:

```powershell
cd backend
uv run pytest -q
```

Expected: all backend tests pass.

- [ ] **Step 4: Run full frontend verification**

Run:

```powershell
cd frontend
npm run build
npm run lint
```

Expected: build and lint pass.

- [ ] **Step 5: Commit migration plan**

Run:

```powershell
git add .gitignore docs/superpowers/plans/2026-05-16-copilotkit-migration.md
git commit -m "docs: plan copilotkit migration"
```

Expected: commit succeeds without staging secrets, `.venv`, `.idea`, or generated frontend bundles.

## Self-Review

- Spec coverage: covers repo hygiene, backend package split, typed data contracts, thesis RAG models, LangGraph state, CopilotKit runtime, React source restoration, GenUI component registry, HITL, and verification.
- Placeholder scan: no undecided markers, no empty task shells.
- Type consistency: thesis models use the same `Claim`, `Evidence`, `Scenario`, and `ClaimReviewAction` names across backend and frontend examples.
- Scope check: this is a migration plan, not an implementation commit. Implementation should happen in small commits following the task order.
