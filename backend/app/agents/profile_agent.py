"""Agent 1 — skill-profile generation (CLAUDE.md §4).

A minimal linear LangGraph pipeline: START -> generate_profile -> END.
The single node calls DeepSeek in JSON mode, then validates the response with
Pydantic (retrying once on malformed JSON / schema mismatch).
"""

import json
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from openai import AsyncOpenAI
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.profile import ProfileGenerationOutput

SYSTEM_PROMPT = """你是一名校园能力画像分析专家，负责根据学生自述与项目经历，生成结构化的技能画像。

请严格按以下规则输出一个 JSON 对象（不要输出 JSON 以外的任何文字、注释或 markdown 代码块）：

1. "skill_vector"：5~8 个技能维度，键为具体技能名，值为 0~1 的打分。
   - 维度要具体（如"后端开发""游戏开发""数据分析""算法基础""前端开发"），禁止使用"编程""学习"这类过于宽泛的词。
2. "interest_tags"：3~6 个兴趣标签（字符串列表）。
3. "potential_directions"：2~3 个潜在方向，每个方向是一个对象，包含两个字段：
   - "direction"：方向名称；
   - "reasoning"：一句话推理依据。

重要约束：
- 不要只总结用户已经做过什么，要推理出"用户可能适合、但尚未明确提到"的方向。
- 每条 reasoning 必须引用用户自述或项目中的具体事实作为依据（例如"做过 EasyX 小游戏，具备实时渲染与图形交互基础，可向游戏客户端开发延伸"）。
- 严禁输出空泛评价，如"该用户能力较强""很有潜力""综合能力不错"这类套话；reasoning 必须是具体的、可操作的。

输出 JSON 结构示例：
{
  "skill_vector": {"后端开发": 0.8, "游戏开发": 0.7, "数据分析": 0.6},
  "interest_tags": ["C++", "游戏开发", "数据分析"],
  "potential_directions": [
    {"direction": "游戏引擎开发", "reasoning": "已有 EasyX 游戏开发经验，具备图形渲染与实时交互基础"},
    {"direction": "数据可视化", "reasoning": "Python 数据分析经历可迁移到可视化方向"}
  ]
}
"""


class ProfileState(TypedDict):
    """State passed through the graph."""

    bio_raw: str
    project_experience: str | None
    result: ProfileGenerationOutput | None


def _build_user_text(bio_raw: str, project_experience: str | None) -> str:
    parts = [f"【学生自述】\n{bio_raw}"]
    if project_experience:
        parts.append(f"【项目经历】\n{project_experience}")
    return "\n\n".join(parts)


class ProfileAgent:
    """LangGraph pipeline that turns raw self-description into a structured profile."""

    def __init__(self) -> None:
        self._client: AsyncOpenAI | None = None
        self._graph = self._build_graph()

    def _get_client(self) -> AsyncOpenAI:
        """Lazily build the DeepSeek client so the app can import without a key."""
        if self._client is None:
            if not settings.deepseek_api_key:
                raise ValueError("DEEPSEEK_API_KEY 未设置，请在 .env 中配置")
            self._client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )
        return self._client

    def _build_graph(self):
        builder = StateGraph(ProfileState)
        builder.add_node("generate_profile", self._generate_profile_node)
        builder.add_edge(START, "generate_profile")
        builder.add_edge("generate_profile", END)
        return builder.compile()

    async def _generate_profile_node(self, state: ProfileState) -> dict:
        user_text = _build_user_text(state["bio_raw"], state["project_experience"])
        result = await self._generate_with_retry(user_text)
        return {"result": result}

    async def _generate_with_retry(self, user_text: str) -> ProfileGenerationOutput:
        last_error: Exception | None = None
        for _ in range(2):  # 1 retry on invalid output, per requirement
            try:
                raw = await self._call_llm(user_text)
                data = json.loads(raw)
                return ProfileGenerationOutput.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
        raise ValueError(f"画像生成失败（LLM 两次返回非法 JSON）：{last_error}")

    async def _call_llm(self, user_text: str) -> str:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    async def ainvoke(
        self, bio_raw: str, project_experience: str | None = None
    ) -> ProfileGenerationOutput:
        state = await self._graph.ainvoke(
            {"bio_raw": bio_raw, "project_experience": project_experience, "result": None}
        )
        return state["result"]


profile_agent = ProfileAgent()
