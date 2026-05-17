from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import json

router = APIRouter(tags=["系统配置"])


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

    try:
        mtime = os.path.getmtime(config_file)
        if not hasattr(load_dify_agents_config, "_cache") or load_dify_agents_config._cache_mtime != mtime:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        load_dify_agents_config._cache = data
                        load_dify_agents_config._cache_mtime = mtime
                        return data
                except Exception:
                    pass
    except Exception:
        pass

    if hasattr(load_dify_agents_config, "_cache"):
        return load_dify_agents_config._cache

    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    raise RuntimeError("配置文件不存在，请创建 data/dify_agents.json")


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
