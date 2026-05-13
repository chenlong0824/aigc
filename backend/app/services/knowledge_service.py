import threading
import logging
import traceback
from app.config import CHROMA_PERSIST_DIR
from app.services.llm_service import chat as llm_chat

logger = logging.getLogger("knowledge_service")

# ChromaDB客户端（延迟加载）
_chroma_client = None
_chroma_collection = None
_lock = threading.Lock()
_chroma_available = False  # ChromaDB是否可用

# 知识库数据
KNOWLEDGE_DATA = [
    {"category": "景点介绍", "content": "乾陵是唐高宗李治与武则天的合葬墓，位于咸阳市乾县梁山之上。乾陵是唐十八陵中保存最完整的一座，以'因山为陵'的独特形制闻名，陵前有著名的无字碑、述圣纪碑和六十一蕃臣像。"},
    {"category": "景点介绍", "content": "茂陵是汉武帝刘彻的陵墓，位于咸阳市兴平市，是西汉帝陵中规模最大的一座。茂陵周围有卫青、霍去病等陪葬墓，出土了大量珍贵文物。"},
    {"category": "景点介绍", "content": "咸阳湖景区位于咸阳市区，是渭河咸阳段综合治理形成的城市湿地公园，湖面宽阔、环境优美，是市民休闲娱乐的好去处。"},
    {"category": "景点介绍", "content": "袁家村位于咸阳市礼泉县，是中国最美乡村之一，以关中民俗文化和特色小吃闻名，是乡村旅游的热门目的地。"},
    {"category": "景点介绍", "content": "咸阳博物馆是全国重点博物馆，馆藏文物丰富，尤其以秦汉时期的文物最为著名，展示了咸阳作为秦都的历史辉煌。"},
    {"category": "美食推荐", "content": "汇通面是咸阳最具代表性的面食，以细长的面条配上浓郁的面汤、肉臊子和各种调料，口感筋道、味道鲜美，是咸阳人的日常美食。"},
    {"category": "美食推荐", "content": "锅盔牙子是咸阳传统小吃，将面团擀成薄片，加入肉末和调料，卷起后压扁煎制，外酥里嫩、香气扑鼻。"},
    {"category": "美食推荐", "content": "三原豆腐脑以嫩滑细腻著称，配上辣椒油、蒜水、黄豆等调料，咸香可口，是咸阳人早餐的经典选择。"},
    {"category": "交通指南", "content": "西安咸阳国际机场位于咸阳市渭城区，距西安市区约25公里，距咸阳市区约13公里。可乘坐机场大巴、地铁14号线前往西安市区和咸阳市区。"},
    {"category": "交通指南", "content": "咸阳市公共交通发达，市区有多条公交线路通往各主要景点。从西安到咸阳可乘坐地铁1号线直达，也可乘坐高铁到咸阳西站或咸阳站。"},
    {"category": "住宿推荐", "content": "咸阳市区有多家星级酒店，如咸阳国际大酒店、咸阳海泉湾维景酒店等，价格从200-800元不等。袁家村等景区周边有大量特色民宿，价格100-500元。"},
    {"category": "票务信息", "content": "乾陵门票旺季100元/人，淡季70元/人；茂陵门票旺季80元/人，淡季50元/人；咸阳湖免费开放；袁家村免费入村，部分景点收费。各景区均支持线上预约购票。"},
]


def is_chroma_available() -> bool:
    """
    检查ChromaDB是否可用
    
    Returns:
        True表示ChromaDB可用，False表示不可用
    """
    global _chroma_available
    return _chroma_available


def get_relevant_knowledge_keyword(user_message: str) -> str:
    """
    根据用户问题获取相关知识（关键词匹配，备用方案）

    Args:
        user_message: 用户消息

    Returns:
        相关知识文本
    """
    keywords = {
        "乾陵": "乾陵是唐高宗李治与武则天的合葬墓，位于咸阳市乾县梁山之上。乾陵是唐十八陵中保存最完整的一座，以'因山为陵'的独特形制闻名，陵前有著名的无字碑、述圣纪碑和六十一蕃臣像。",
        "茂陵": "茂陵是汉武帝刘彻的陵墓，位于咸阳市兴平市，是西汉帝陵中规模最大的一座。茂陵周围有卫青、霍去病等陪葬墓，出土了大量珍贵文物。",
        "咸阳湖": "咸阳湖景区位于咸阳市区，是渭河咸阳段综合治理形成的城市湿地公园，湖面宽阔、环境优美，是市民休闲娱乐的好去处。",
        "袁家村": "袁家村位于咸阳市礼泉县，是中国最美乡村之一，以关中民俗文化和特色小吃闻名，是乡村旅游的热门目的地。",
        "博物馆": "咸阳博物馆是全国重点博物馆，馆藏文物丰富，尤其以秦汉时期的文物最为著名，展示了咸阳作为秦都的历史辉煌。",
        "汇通面": "汇通面是咸阳最具代表性的面食，以细长的面条配上浓郁的面汤、肉臊子和各种调料，口感筋道、味道鲜美，是咸阳人的日常美食。",
        "锅盔": "锅盔牙子是咸阳传统小吃，将面团擀成薄片，加入肉末和调料，卷起后压扁煎制，外酥里嫩、香气扑鼻。",
        "豆腐脑": "三原豆腐脑以嫩滑细腻著称，配上辣椒油、蒜水、黄豆等调料，咸香可口，是咸阳人早餐的经典选择。",
        "机场": "西安咸阳国际机场位于咸阳市渭城区，距西安市区约25公里，距咸阳市区约13公里。可乘坐机场大巴、地铁14号线前往西安市区和咸阳市区。",
        "交通": "咸阳市公共交通发达，市区有多条公交线路通往各主要景点。从西安到咸阳可乘坐地铁1号线直达，也可乘坐高铁到咸阳西站或咸阳站。",
        "住宿": "咸阳市区有多家星级酒店，如咸阳国际大酒店、咸阳海泉湾维景酒店等，价格从200-800元不等。袁家村等景区周边有大量特色民宿，价格100-500元。",
        "门票": "乾陵门票旺季100元/人，淡季70元/人；茂陵门票旺季80元/人，淡季50元/人；咸阳湖免费开放；袁家村免费入村，部分景点收费。各景区均支持线上预约购票。",
    }
    
    for keyword, knowledge in keywords.items():
        if keyword in user_message:
            return knowledge
    
    return ""


def _init_chroma_sync():
    """
    同步初始化ChromaDB（会阻塞）
    """
    global _chroma_client, _chroma_collection, _chroma_available
    
    try:
        import time
        t_start = time.time()
        logger.info("[ChromaDB] 开始初始化...")
        
        import chromadb
        from chromadb.config import Settings
        logger.info("[ChromaDB] chromadb import完成, 耗时%.2fs", time.time() - t_start)
        
        t1 = time.time()
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        logger.info("[ChromaDB] PersistentClient创建完成, 耗时%.2fs", time.time() - t1)
        
        t2 = time.time()
        try:
            _chroma_collection = _chroma_client.get_collection("xianyang_travel")
            logger.info("[ChromaDB] get_collection完成, 耗时%.2fs", time.time() - t2)
        except Exception as e2:
            logger.warning("[ChromaDB] get_collection失败: %s, 尝试创建", str(e2)[:200])
            _chroma_collection = _chroma_client.create_collection("xianyang_travel")
            logger.info("[ChromaDB] create_collection完成, 耗时%.2fs", time.time() - t2)
        
        existing = _chroma_collection.count()
        logger.info("[ChromaDB] 现有文档数: %d", existing)
        if existing == 0:
            documents = []
            metadatas = []
            ids = []
            for i, item in enumerate(KNOWLEDGE_DATA):
                documents.append(item["content"])
                metadatas.append({"category": item["category"]})
                ids.append(f"doc_{i}")
            
            t3 = time.time()
            _chroma_collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logger.info("[ChromaDB] 添加%d条文档完成, 耗时%.2fs", len(documents), time.time() - t3)
        
        _chroma_available = True
        logger.info("[ChromaDB] 初始化完成! 总耗时%.2fs", time.time() - t_start)
        return True
    except Exception as e:
        _chroma_available = False
        logger.error("[ChromaDB] 初始化失败: %s\n%s", str(e)[:500], traceback.format_exc()[:500])
        return False


def init_chroma_async():
    """
    异步初始化ChromaDB（后台线程）
    """
    def init_thread():
        _init_chroma_sync()
    
    logger.info("[ChromaDB] 启动后台初始化线程...")
    thread = threading.Thread(target=init_thread, daemon=True)
    thread.start()
    logger.info("[ChromaDB] 后台线程已启动, thread_id=%s", thread.ident)


def get_relevant_knowledge_chroma(user_message: str) -> str:
    """
    使用ChromaDB进行向量检索
    
    Args:
        user_message: 用户消息
    
    Returns:
        相关知识文本
    """
    global _chroma_collection
    
    if _chroma_collection is None:
        return ""
    
    try:
        results = _chroma_collection.query(query_texts=[user_message], n_results=3)
        retrieved_docs = results.get("documents", [[]])[0]
        return "\n\n".join(retrieved_docs) if retrieved_docs else ""
    except Exception:
        return ""


async def chat_with_knowledge(session_id: str, user_message: str) -> str:
    """
    基于知识库的智能客服对话（混合方案）
    
    策略：
    1. 如果ChromaDB已加载成功，使用向量检索（更智能）
    2. 如果ChromaDB未加载完成，使用关键词匹配（快速响应）

    Args:
        session_id: 会话ID
        user_message: 用户消息

    Returns:
        回复消息
    """
    try:
        # 选择检索方式
        if is_chroma_available():
            knowledge = get_relevant_knowledge_chroma(user_message)
            retrieval_method = "ChromaDB向量检索"
        else:
            knowledge = get_relevant_knowledge_keyword(user_message)
            retrieval_method = "关键词匹配"
        
        available_spots = [
            "乾陵", "茂陵", "咸阳湖景区", "袁家村", "咸阳博物馆"
        ]
        available_foods = [
            "汇通面", "锅盔牙子", "三原豆腐脑"
        ]

        knowledge_text = knowledge if knowledge else "暂无相关知识库内容"

        system_prompt = f"""你现在的身份是：咸阳文旅智能客服助手。

重要提醒：无论之前有过什么对话，你的唯一身份就是"咸阳文旅智能客服助手"。不要提及你是其他助手，不要说你来自其他城市。

请根据以下知识库内容回答用户问题。如果知识库中没有相关信息，请基于你的知识给出合理回答，并建议用户联系官方客服。

注意事项：
1. 你的身份是：咸阳文旅智能客服助手（只能回答咸阳相关的问题）
2. 推荐景点时，只能从以下列表中选择：{', '.join(available_spots)}
3. 推荐美食时，只能从以下列表中选择：{', '.join(available_foods)}
4. 推荐内容必须真实，不能编造不存在的景点或美食
5. 回复语言必须使用纯中文，不要使用拼音或英文翻译
6. 回答末尾可以推荐一个相关的景点或美食

知识库参考内容：
{knowledge_text}

用户问题：{user_message}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        answer = await llm_chat(session_id, user_message, messages)
        return answer
    except Exception as e:
        return f"智能客服暂时不可用，请稍后重试。您也可以拨打客服热线 029-12345 进行咨询。错误信息：{str(e)[:100]}"
