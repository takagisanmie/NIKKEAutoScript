class Effect:
    def __init__(self, name, displayName, priority, type, quality, shape):
        self.name = name
        self.displayName = displayName
        self.priority = priority
        # 攻击，防御，辅助
        self.type = type
        # 品质
        self.quality = quality
        # 形状
        self.shape = shape

    pass
