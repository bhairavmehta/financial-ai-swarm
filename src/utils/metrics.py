"""
Metrics collection for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, Summary
from functools import wraps
import time
from typing import Callable


# Define metrics
transaction_counter = Counter(
    'financial_swarm_transactions_total',
    'Total number of transactions processed',
    ['agent', 'status']
)

agent_latency = Histogram(
    'financial_swarm_agent_latency_seconds',
    'Agent processing latency',
    ['agent'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

fraud_score_gauge = Gauge(
    'financial_swarm_fraud_score',
    'Latest fraud score',
    ['risk_level']
)

compliance_checks = Counter(
    'financial_swarm_compliance_checks_total',
    'Total compliance checks',
    ['status', 'sanctions_hit', 'pep_hit']
)

api_request_duration = Summary(
    'financial_swarm_api_request_duration_seconds',
    'API request duration'
)

active_agents = Gauge(
    'financial_swarm_active_agents',
    'Number of active agent processes',
    ['agent']
)


def track_agent_latency(agent_name: str):
    """
    Decorator to track agent execution latency

    Args:
        agent_name: Name of the agent

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                latency = time.time() - start_time
                agent_latency.labels(agent=agent_name).observe(latency)
                transaction_counter.labels(agent=agent_name, status=status).inc()
        return wrapper
    return decorator


def record_fraud_score(risk_level: str, score: float):
    """Record fraud score metric"""
    fraud_score_gauge.labels(risk_level=risk_level).set(score)


def record_compliance_check(status: str, sanctions_hit: bool, pep_hit: bool):
    """Record compliance check metric"""
    compliance_checks.labels(
        status=status,
        sanctions_hit=str(sanctions_hit),
        pep_hit=str(pep_hit)
    ).inc()


def update_active_agents(agent_name: str, count: int):
    """Update active agents gauge"""
    active_agents.labels(agent=agent_name).set(count)
