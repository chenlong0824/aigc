from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import json

router = APIRouter(prefix="/api/config", tags=["系统配置"])


class DifyAgent(BaseModel):
    id: str
    name: str
    description: str
    icon: Optional[str] = "RobotOutlined"
    token: str
    baseUrl: str


class DifyAgentsConfig(BaseModel):
    agents: List[DifyAgent]


def load_dify_agents_config():
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "dify_agents.json")

    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    default_config = {
        "agents": [
            {
                "id": "default",
                "name": "默认助手",
                "description": "默认Dify助手",
                "icon": "RobotOutlined",
                "token": "",
                "baseUrl": "http://localhost"
            }
        ]
    }

    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

    return default_config


@router.get("/dify-agents")
def get_dify_agents():
    return load_dify_agents_config()


@router.post("/dify-agents")
def update_dify_agents(config: DifyAgentsConfig):
    config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "dify_agents.json")

    os.makedirs(os.path.dirname(config_file), exist_ok=True)

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)

    return {"status": "ok", "message": "配置已保存，重启服务后生效"}
