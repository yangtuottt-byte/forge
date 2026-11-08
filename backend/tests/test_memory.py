from app.agents.base.memory import Memory


def test_memory_add_get():
    """add 存,get_all 取"""
    mem = Memory()
    mem.add("user", "你好")
    mem.add("assistant", "你好!有什么可以帮你?")
    assert len(mem.get_all()) == 2
    assert mem.get_all()[0] == {"role": "user", "content": "你好"}


def test_memory_clear():
    """clear 清空"""
    mem = Memory()
    mem.add("user", "你好")
    mem.clear()
    assert mem.get_all() == []


def test_memory_multi_turn():
    """多轮:每轮都存,get_all 取全部"""
    mem = Memory()
    mem.add("user", "1+1")
    mem.add("assistant", "2")
    mem.add("user", "那2+2")
    mem.add("assistant", "4")
    history = mem.get_all()
    assert len(history) == 4
    # 第 3 条是第 2 轮的用户提问
    assert history[2]["content"] == "那2+2"
