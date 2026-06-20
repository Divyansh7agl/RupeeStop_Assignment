"""
Investment Committee Agent - FastAPI Backend
Endpoints:
  POST /analyze        - Full pipeline, returns complete JSON
  POST /analyze/stream - SSE stream of pipeline logs + final result
  GET  /portfolio      - Returns sample portfolio data
  GET  /health         - Health check
"""

from dotenv import load_dotenv
load_dotenv()

import json
import time
import asyncio
import os
import sys
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from models.schemas import QueryRequest, FinalRecommendation, PipelineLog
from agents.llm_client import LLMClient
from agents.planner import PlannerAgent
from data.portfolio import SAMPLE_PORTFOLIO

# ── Structured logging setup ──
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory()
)
logger = structlog.get_logger(__name__)

# ── App lifecycle ──
llm_client: LLMClient = None
planner: PlannerAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global llm_client, planner
    logger.info("app.startup")
    try:
        llm_client = LLMClient()
        planner = PlannerAgent(llm_client)
        logger.info("app.ready")
    except Exception as e:
        logger.error("app.startup_failed", error=str(e))
        raise
    yield
    logger.info("app.shutdown")


app = FastAPI(
    title="Investment Committee Agent",
    description="Multi-agent AI system simulating an investment committee with Conservative, Growth, Cost Efficiency, and Devil's Advocate advisors.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "llm_ready": llm_client is not None,
        "timestamp": time.time()
    }


@app.get("/portfolio")
async def get_sample_portfolio():
    """Returns the sample portfolio used for analysis."""
    return SAMPLE_PORTFOLIO


@app.post("/analyze", response_model=FinalRecommendation)
async def analyze(request: QueryRequest):
    """
    Runs the full multi-agent pipeline and returns the complete recommendation.
    Blocking — waits for all agents to complete.
    """
    if not planner:
        raise HTTPException(status_code=503, detail="Service not ready. LLM client not initialized.")

    logger.info("api.analyze.start", question=request.question[:100])
    start = time.time()

    try:
        result, logs = await planner.run(request)
        duration = round((time.time() - start) * 1000, 2)
        logger.info("api.analyze.complete", duration_ms=duration, confidence=result.confidence_score)
        return result
    except Exception as e:
        logger.error("api.analyze.failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.post("/analyze/stream")
async def analyze_stream(request: QueryRequest):
    """
    SSE streaming endpoint. Yields pipeline step updates in real-time,
    then the final result as the last event.
    """
    if not planner:
        raise HTTPException(status_code=503, detail="Service not ready.")

    async def event_generator():
        logger.info("api.stream.start", question=request.question[:100])

        # We run the pipeline and yield step events
        steps_done = []
        pipeline_steps = [
            ("load_profile", "Loading investor profile..."),
            ("planner", "Planner analyzing question..."),
            ("tool_execution", "Running financial tools..."),
            ("specialists_parallel", "Conservative, Growth & Cost advisors working in parallel..."),
            ("devils_advocate", "Devil's Advocate challenging the committee..."),
            ("consensus", "Consensus Agent synthesizing final recommendation..."),
            ("pipeline_complete", "Complete!")
        ]

        # Emit each step as it starts
        for step_id, step_msg in pipeline_steps:
            event = {
                "type": "step_update",
                "step": step_id,
                "status": "running",
                "message": step_msg
            }
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.1)  # allow event to flush

        # Run the actual pipeline
        try:
            result, logs = await planner.run(request)

            # Emit completed steps from logs
            for log in logs:
                event = {
                    "type": "step_update",
                    "step": log.step,
                    "status": log.status,
                    "message": log.details or ""
                }
                yield f"data: {json.dumps(event)}\n\n"

            # Final result event
            final_event = {
                "type": "final_result",
                "data": result.model_dump()
            }
            yield f"data: {json.dumps(final_event)}\n\n"

        except Exception as e:
            error_event = {
                "type": "error",
                "message": str(e)
            }
            yield f"data: {json.dumps(error_event)}\n\n"
            logger.error("api.stream.error", error=str(e))

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )