"""
Core Orchestration Supervisor
Based on LangGraph supervisor pattern with Oracle MCP architecture
"""

from typing import Annotated, Sequence, TypedDict, Literal, Optional
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
import operator
from dataclasses import dataclass
from datetime import datetime
import logging

# Import all agents
from src.agents.fraud_detection.agent import get_fraud_agent
from src.agents.compliance.agent import get_compliance_agent
from src.agents.spend_analysis.agent import get_spend_agent
from src.agents.vendor_analysis.agent import get_vendor_agent
from src.agents.explanation.agent import get_explanation_agent
from src.agents.learning.agent import get_learning_agent

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    transaction_data: dict
    fraud_score: float
    compliance_status: str
    document_data: dict
    spend_analysis: dict
    vendor_analysis: dict
    explanation: str
    agent_decisions: list


@dataclass
class AgentConfig:
    """Configuration for each agent"""
    name: str
    description: str
    priority: int
    timeout: int = 30


class FinancialOrchestrator:
    """
    Main orchestrator for financial AI agents
    Implements supervisor pattern from LangGraph
    """
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", use_llm: bool = False):
        self.use_llm = use_llm
        if use_llm:
            self.model = ChatOpenAI(model=model_name, temperature=0)
        else:
            self.model = None
        self.agents = self._initialize_agents()
        self.agent_instances = self._load_agent_instances()
        self.graph = self._build_graph()
        
    def _initialize_agents(self) -> dict:
        """Initialize all specialized agents"""
        return {
            "fraud_detection": AgentConfig(
                name="fraud_detection",
                description="Detects fraudulent transactions using ML models",
                priority=1
            ),
            "compliance": AgentConfig(
                name="compliance",
                description="Checks OFAC/PEP compliance and regulatory rules",
                priority=2
            ),
            "spend_analysis": AgentConfig(
                name="spend_analysis",
                description="Analyzes spending patterns and budget compliance",
                priority=3
            ),
            "vendor_analysis": AgentConfig(
                name="vendor_analysis",
                description="Evaluates vendor risk and payment patterns",
                priority=4
            ),
            "explanation": AgentConfig(
                name="explanation",
                description="Generates human-readable explanations of decisions",
                priority=5
            ),
            "learning": AgentConfig(
                name="learning",
                description="Learns from feedback and improves models",
                priority=6
            )
        }

    def _load_agent_instances(self) -> dict:
        """Load actual agent instances"""
        logger.info("Loading agent instances")
        return {
            "fraud_detection": get_fraud_agent(),
            "compliance": get_compliance_agent(),
            "spend_analysis": get_spend_agent(),
            "vendor_analysis": get_vendor_agent(),
            "explanation": get_explanation_agent(),
            "learning": get_learning_agent()
        }
    
    def _create_supervisor_prompt(self) -> str:
        """Create the supervisor routing prompt"""
        agent_descriptions = "\n".join([
            f"- {name}: {config.description}"
            for name, config in self.agents.items()
        ])
        
        return f"""You are a supervisor managing a team of specialized financial AI agents.
        
Available agents:
{agent_descriptions}

Given the current state and user request, determine which agent should act next.
Consider:
1. Agent priorities and dependencies
2. Current transaction state
3. Which analyses are still needed

Respond with the name of the agent to route to, or 'FINISH' if complete.
"""
    
    def supervisor_node(self, state: AgentState) -> dict:
        """Supervisor decides which agent to route to next"""
        messages = [
            {"role": "system", "content": self._create_supervisor_prompt()},
            {"role": "user", "content": self._format_state(state)}
        ]
        
        response = self.model.invoke(messages)
        next_agent = response.content.strip()
        
        # Validate agent exists
        if next_agent not in self.agents and next_agent != "FINISH":
            logger.warning(f"Invalid agent routing: {next_agent}, defaulting to fraud_detection")
            next_agent = "fraud_detection"
        
        logger.info(f"Supervisor routing to: {next_agent}")
        return {"next": next_agent}
    
    def _format_state(self, state: AgentState) -> str:
        """Format state for supervisor decision making"""
        return f"""
Current Transaction State:
- Transaction Data: {state.get('transaction_data', {})}
- Fraud Score: {state.get('fraud_score', 'Not analyzed')}
- Compliance Status: {state.get('compliance_status', 'Not checked')}
- Spend Analysis: {state.get('spend_analysis', 'Not performed')}
- Vendor Analysis: {state.get('vendor_analysis', 'Not performed')}
- Explanation: {state.get('explanation', 'Not generated')}

Completed Agents: {[d['agent'] for d in state.get('agent_decisions', [])]}
"""
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self.supervisor_node)
        
        # Add agent nodes (will be connected to actual implementations)
        for agent_name in self.agents.keys():
            workflow.add_node(agent_name, self._create_agent_node(agent_name))
        
        # Add conditional edges from supervisor to agents
        workflow.add_conditional_edges(
            "supervisor",
            lambda x: x["next"],
            {name: name for name in self.agents.keys()} | {"FINISH": END}
        )
        
        # All agents route back to supervisor
        for agent_name in self.agents.keys():
            workflow.add_edge(agent_name, "supervisor")
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        return workflow.compile()
    
    def _create_agent_node(self, agent_name: str):
        """Create a node function for a specific agent"""
        def agent_node(state: AgentState) -> dict:
            """Execute the specific agent logic"""
            logger.info(f"Executing agent: {agent_name}")

            transaction_data = state.get("transaction_data", {})
            agent_instance = self.agent_instances.get(agent_name)

            result_update = {
                "messages": [HumanMessage(content=f"{agent_name} processed")],
                "agent_decisions": state.get("agent_decisions", [])
            }

            try:
                # Execute specific agent logic
                if agent_name == "fraud_detection":
                    fraud_result = agent_instance.detect_fraud(transaction_data)
                    result_update["fraud_score"] = fraud_result.overall_score
                    result_update["agent_decisions"].append({
                        "agent": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "result": {
                            "risk_level": fraud_result.risk_level,
                            "overall_score": fraud_result.overall_score,
                            "risk_factors": fraud_result.risk_factors,
                            "confidence": fraud_result.confidence
                        }
                    })

                elif agent_name == "compliance":
                    compliance_result = agent_instance.check_compliance(transaction_data)
                    result_update["compliance_status"] = compliance_result.status
                    result_update["agent_decisions"].append({
                        "agent": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "result": {
                            "status": compliance_result.status,
                            "risk_score": compliance_result.risk_score,
                            "sanctions_hit": compliance_result.sanctions_hit,
                            "pep_hit": compliance_result.pep_hit,
                            "findings": compliance_result.policy_violations
                        }
                    })

                elif agent_name == "spend_analysis":
                    # Get historical transactions for analysis
                    transactions = [transaction_data]  # In production, fetch historical data
                    spend_result = agent_instance.analyze_spending(transactions)
                    result_update["spend_analysis"] = {
                        "budget_status": spend_result.budget_status,
                        "anomalies": spend_result.anomalies,
                        "recommendations": spend_result.recommendations
                    }
                    result_update["agent_decisions"].append({
                        "agent": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "result": {
                            "budget_utilization": spend_result.budget_utilization,
                            "anomaly_count": len(spend_result.anomalies),
                            "over_budget_categories": spend_result.over_budget_categories
                        }
                    })

                elif agent_name == "vendor_analysis":
                    merchant = transaction_data.get("merchant", "Unknown")
                    # In production, fetch all transactions for this vendor
                    vendor_transactions = [transaction_data]
                    vendor_result = agent_instance.analyze_vendor(merchant, vendor_transactions)
                    result_update["vendor_analysis"] = {
                        "vendor_name": vendor_result.vendor_name,
                        "risk_level": vendor_result.risk_level,
                        "risk_score": vendor_result.risk_score,
                        "total_spend": vendor_result.total_spend,
                        "recommendations": vendor_result.recommendations
                    }
                    result_update["agent_decisions"].append({
                        "agent": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "result": {
                            "risk_level": vendor_result.risk_level,
                            "risk_factors": vendor_result.risk_factors,
                            "duplicate_likelihood": vendor_result.duplicate_likelihood
                        }
                    })

                elif agent_name == "explanation":
                    # Generate comprehensive explanation of all results
                    all_results = {
                        "fraud_detection": state.get("fraud_score", 0),
                        "compliance": state.get("compliance_status", "pending"),
                        "spend_analysis": state.get("spend_analysis", {}),
                        "vendor_analysis": state.get("vendor_analysis", {})
                    }

                    # Find fraud decision for detailed explanation
                    fraud_decision = next(
                        (d["result"] for d in state.get("agent_decisions", [])
                         if d["agent"] == "fraud_detection"),
                        None
                    )

                    if fraud_decision:
                        explanation_result = agent_instance.explain_fraud_detection(
                            transaction_data, fraud_decision
                        )
                        result_update["explanation"] = explanation_result.summary
                        result_update["agent_decisions"].append({
                            "agent": agent_name,
                            "timestamp": datetime.now().isoformat(),
                            "result": {
                                "title": explanation_result.title,
                                "summary": explanation_result.summary,
                                "key_points": explanation_result.key_points,
                                "recommendations": explanation_result.recommendations
                            }
                        })

                elif agent_name == "learning":
                    # Learning agent monitors and improves - no immediate action needed
                    performance = agent_instance.get_agent_performance()
                    result_update["agent_decisions"].append({
                        "agent": agent_name,
                        "timestamp": datetime.now().isoformat(),
                        "result": {
                            "performance_summary": performance,
                            "status": "monitoring"
                        }
                    })

                logger.info(f"Agent {agent_name} completed successfully")

            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
                result_update["agent_decisions"].append({
                    "agent": agent_name,
                    "timestamp": datetime.now().isoformat(),
                    "result": {"error": str(e), "status": "failed"}
                })

            return result_update

        return agent_node
    
    async def process_transaction(self, transaction_data: dict) -> dict:
        """
        Main entry point for transaction processing
        
        Args:
            transaction_data: Transaction details including amount, merchant, etc.
            
        Returns:
            Complete analysis results from all agents
        """
        initial_state = AgentState(
            messages=[HumanMessage(content=f"Process transaction: {transaction_data}")],
            next="supervisor",
            transaction_data=transaction_data,
            fraud_score=0.0,
            compliance_status="pending",
            document_data={},
            spend_analysis={},
            vendor_analysis={},
            explanation="",
            agent_decisions=[]
        )
        
        logger.info(f"Starting orchestration for transaction: {transaction_data.get('transaction_id')}")
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            return self._format_results(final_state)
        except Exception as e:
            logger.error(f"Orchestration error: {e}", exc_info=True)
            raise
    
    def _format_results(self, state: AgentState) -> dict:
        """Format final results for API response"""
        return {
            "transaction_id": state["transaction_data"].get("transaction_id"),
            "fraud_score": state.get("fraud_score", 0.0),
            "compliance_status": state.get("compliance_status", "pending"),
            "spend_analysis": state.get("spend_analysis", {}),
            "vendor_analysis": state.get("vendor_analysis", {}),
            "explanation": state.get("explanation", ""),
            "agent_decisions": state.get("agent_decisions", []),
            "status": "completed"
        }
    
    def visualize_graph(self, output_path: str = "orchestration_graph.png"):
        """Visualize the orchestration graph"""
        try:
            from langchain_core.runnables.graph import MermaidDrawMethod
            graph_image = self.graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            with open(output_path, "wb") as f:
                f.write(graph_image)
            logger.info(f"Graph visualization saved to {output_path}")
        except Exception as e:
            logger.warning(f"Could not generate graph visualization: {e}")


# Global orchestrator instance
orchestrator = None

def get_orchestrator() -> FinancialOrchestrator:
    """Get or create global orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = FinancialOrchestrator()
    return orchestrator


if __name__ == "__main__":
    # Test the orchestrator
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    test_transaction = {
        "transaction_id": "TXN-TEST-001",
        "amount": 15000.00,
        "merchant": "Tech Vendor Inc",
        "category": "IT Services",
        "user_id": "EMP-001"
    }
    
    orch = FinancialOrchestrator()
    result = asyncio.run(orch.process_transaction(test_transaction))
    print(f"Result: {result}")
