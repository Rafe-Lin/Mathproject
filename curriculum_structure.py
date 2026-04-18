"""
课程结构定义与依赖关系
定义学生应该按照的学习路径
"""

# =============================================
# 课程年级与技能分组
# =============================================

CURRICULUM_GRADES = {
    '一上': {
        'label': 'jh_數學1上',
        'sequence_order': 1,
        'skills': [
            'jh_數學1上_CommonDivisibilityRules',
            'jh_數學1上_FourArithmeticOperationsOfIntegers',
            'jh_數學1上_IntegerAdditionOperation',
        ]
    },
    '一下': {
        'label': 'jh_數學1下',
        'sequence_order': 2,
        'skills': [
            'jh_數學1下_DrawingGraphsOfTwoVariableLinearEquations',
            'jh_數學1下_RectangularCoordinatePlaneAndCoordinateRepresentation',
        ],
        'prerequisites': ['一上']
    },
    '二上': {
        'label': 'jh_數學2上',
        'sequence_order': 3,
        'skills': [
            'jh_數學2上_BasicPropertiesOfRadicalOperations',
            'jh_數學2上_FourOperationsOfRadicals',
            'jh_數學2上_PolynomialAdditionAndSubtraction',
            'jh_數學2上_PolynomialDivision',
            'jh_數學2上_WordProblems',
        ],
        'prerequisites': ['一上', '一下']
    },
    '二下': {
        'label': 'jh_數學2下',
        'sequence_order': 4,
        'skills': [
            'jh_數學2下_IdentifyingAndConstructingParallelograms',
            'jh_數學2下_MeaningAndPropertiesOfParallelograms',
            'jh_數學2下_PropertiesOfRectanglesRhombusesKitesAndSquares',
        ],
        'prerequisites': ['一上', '一下', '二上']
    },
    '三上': {
        'label': 'jh_數學3上',
        'sequence_order': 5,
        'skills': [
            'jh_數學3上_ApplicationOfParallelLinesProportionalSegmentsProperty',
            'jh_數學3上_GeometricProof',
            'jh_數學3上_InscribedAngleParallelChordsAndCyclicQuadrilateral',
            'jh_數學3上_ParallelLinesProportionalSegmentsProperty',
        ],
        'prerequisites': ['一上', '一下', '二上', '二下']
    }
}

# 建立快速查询表
SKILL_TO_GRADE = {}
SKILL_TO_SEQUENCE_ORDER = {}

for grade_name, grade_info in CURRICULUM_GRADES.items():
    for skill in grade_info['skills']:
        SKILL_TO_GRADE[skill] = grade_name
        SKILL_TO_SEQUENCE_ORDER[skill] = grade_info['sequence_order']


# =============================================
# 课程进度定义（学生应该如何推进）
# =============================================

class CurriculumProgress:
    """
    定义学生的课程进度阶段
    
    目标：
    1. 确保时序性：学生必须按照年级顺序学习
    2. 允许重复练习：但大方向是递进的
    3. 允许少量"回顾"：但不会到下级太多
    """
    
    # 学生可能在的阶段
    STAGES = [
        {'name': '一上学习', 'grades': ['一上'], 'duration_pct': 0.20},
        {'name': '一下学习', 'grades': ['一上', '一下'], 'duration_pct': 0.20},
        {'name': '二上学习', 'grades': ['一上', '一下', '二上'], 'duration_pct': 0.20},
        {'name': '二下学习', 'grades': ['一上', '一下', '二上', '二下'], 'duration_pct': 0.20},
        {'name': '三上学习', 'grades': ['一上', '一下', '二上', '二下', '三上'], 'duration_pct': 0.20},
    ]
    
    @staticmethod
    def get_allowed_grades(progress_ratio):
        """
        根据学生的进度比例，返回允许的年级范围
        
        Args:
            progress_ratio: 学生的进度 [0, 1]
        
        Returns:
            allowed_grades: 允许学生学习的年级列表
        """
        cumsum = 0
        for stage in CurriculumProgress.STAGES:
            cumsum += stage['duration_pct']
            if progress_ratio <= cumsum:
                return stage['grades']
        return ['一上', '一下', '二上', '二下', '三上']  # 学完所有


# =============================================
# 数据验证工具
# =============================================

def validate_sequence(skill_sequence):
    """
    验证技能序列是否符合课程要求
    
    返回值：
    {
        'is_valid': bool,
        'violations': int,
        'max_backjump': int,  # 最大的回跳幅度
        'grade_sequence': list,
    }
    """
    grades = [SKILL_TO_GRADE[skill] for skill in skill_sequence]
    orders = [SKILL_TO_SEQUENCE_ORDER[skill] for skill in skill_sequence]
    
    violations = 0
    max_backjump = 0
    
    for i in range(len(orders) - 1):
        if orders[i] > orders[i+1]:  # 回跳
            violations += 1
            backjump = orders[i] - orders[i+1]
            max_backjump = max(max_backjump, backjump)
    
    is_valid = (violations == 0)
    
    return {
        'is_valid': is_valid,
        'violations': violations,
        'max_backjump': max_backjump,
        'grade_sequence': grades,
        'order_sequence': orders,
    }


if __name__ == "__main__":
    print("课程结构定义已加载")
    print(f"总年级数：{len(CURRICULUM_GRADES)}")
    print(f"总技能数：{sum(len(g['skills']) for g in CURRICULUM_GRADES.values())}")
    print("\n年级顺序：")
    for grade_name, info in CURRICULUM_GRADES.items():
        print(f"  {info['sequence_order']}. {grade_name}: {len(info['skills'])} 个技能")
