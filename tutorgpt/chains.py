from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatLiteLLM
from langchain.schema.runnable import RunnableSequence
from tutorgpt.logger import time_logger
from tutorgpt.prompts import (
    LEARNING_TUTOR_INCEPTION_PROMPT,
    STAGE_ANALYZER_INCEPTION_PROMPT,
)


class StageAnalyzerChain:
    """Chain to analyze which stage the learning roadmap conversation should move into."""

    @classmethod
    @time_logger
    def from_llm(cls, llm: ChatLiteLLM) -> RunnableSequence:
        """Get the response parser for analyzing the learning stage using RunnableSequence."""
        stage_analyzer_prompt = PromptTemplate(
            template=STAGE_ANALYZER_INCEPTION_PROMPT,
            input_variables=[
                "conversation_history",
                "conversation_stage_id",
                "conversation_stages",
            ],
        )
        print(f"STAGE ANALYZER PROMPT {stage_analyzer_prompt}")

        return stage_analyzer_prompt | llm


class LearningTutorConversationChain:
    """Chain to generate the next response in the learning tutor conversation."""

    @classmethod
    @time_logger
    def from_llm(
        cls,
        llm: ChatLiteLLM,
    ) -> RunnableSequence:
        """Get the response parser for tutoring conversations using RunnableSequence."""
        tutor_agent_prompt = LEARNING_TUTOR_INCEPTION_PROMPT
        prompt = PromptTemplate(
            template=tutor_agent_prompt,
            input_variables=[
                "tutor_name",
                "conversation_history",
            ],
        )

        return prompt | llm

