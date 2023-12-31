from pandas import DataFrame


# 得分计算单元
# 每种会有做多得分和做空计算
class ScorePass:

    def __init__(self, score_weight: float = 1):
        # 设置权重，默认值为1
        self.score_weight = score_weight

    # 得分归一化
    # input->+inf, output->1
    # input->0, output->0
    # input->-inf, output = 0
    @staticmethod
    def normalization(score: float) -> float:
        if score < 0:
            return 0

        # (x+1) * (y-1) = -1
        # y = -1/(x+1) + 1
        return -1 / (score + 1) + 1

    # 数据输入数据计算做多
    def run_up(self, df: DataFrame) -> float:
        pass

    # 数据输入数据计算做空
    def run_down(self, df: DataFrame) -> float:
        pass

    def up_score(self, df: DataFrame) -> float:
        return self.normalization(self.run_up(df)) * self.score_weight

    def down_score(self, df: DataFrame) -> float:
        return self.normalization(self.run_down(df)) * self.score_weight

    # 设置权重
    def set_wight(self, weight: float):
        self.score_weight = weight


# 限制单元
class LimitPass(ScorePass):
    def __init__(self, score_weight: float = 1):
        super().__init__(score_weight=score_weight)

    def run_up(self, df: DataFrame) -> bool:
        pass

    def run_down(self, df: DataFrame) -> bool:
        pass

    def up_score(self, df: DataFrame) -> float:
        if not self.run_up(df):
            return -float('inf')
        return 0

    def down_score(self, df: DataFrame) -> float:
        if not self.run_down(df):
            return -float('inf')
        return 0


# 得分计算系统
class ScorePassManager:

    def __init__(self):
        # 设置得分计算单元列表
        self.score_pass_list: [ScorePass] = []

    # 做多得分
    def run_up(self, df: DataFrame, ) -> float:
        score = 0.0
        for score_pass in self.score_pass_list:
            score += score_pass.up_score(df)
        return score

    # 做空得分
    def run_down(self, df: DataFrame, ) -> float:
        score = 0.0
        for score_pass in self.score_pass_list:
            score += score_pass.down_score(df)
        return score

    # 添加得分计算单元
    def add_score_pass(self, score_pass: ScorePass):
        self.score_pass_list.append(score_pass)
