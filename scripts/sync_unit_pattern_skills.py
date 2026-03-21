# -*- coding: utf-8 -*-
# ==============================================================================
# ID: sync_unit_pattern_skills.py
# Description:
#   產生「單元 base + 題型 delta」的技能程式碼。
#   讀取 agent_skills/<unit_id>/SKILL.md + patterns/<pattern_id>.md，
#   合併後交給 code_generator 生成 skills/<unit_id>__<pattern_id>.py
#
# Usage:
#   python scripts/sync_unit_pattern_skills.py --unit <unit_id> --pattern <pattern_id>
#   python scripts/sync_unit_pattern_skills.py --unit <unit_id> --all
#   python scripts/sync_unit_pattern_skills.py --unit <unit_id> --all --mode benchmark
# ==============================================================================

import os
import sys
import argparse
from datetime import datetime
from tqdm import tqdm

# 強制使用 AST Pipeline
os.environ['USE_AST_PIPELINE'] = '1'

# ==============================================================================
# 智慧路徑設定
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)

from app import create_app
from core.code_generator import auto_generate_skill_code
from core.code_utils.unit_spec_loader import (
    build_unit_pattern_spec,
    list_patterns_for_unit,
    make_pattern_skill_id,
)
from core.code_utils.file_utils import path_in_root


def _generate_one(unit_id: str, pattern_id: str, mode: str = None, overwrite: bool = True) -> tuple:
    """
    生成單一 pattern skill。

    Returns:
        (success: bool, message: str)
    """
    skill_id = make_pattern_skill_id(unit_id, pattern_id)
    out_path = path_in_root('skills', f'{skill_id}.py')

    if os.path.isfile(out_path) and not overwrite:
        return False, f"已存在且未指定覆寫: {out_path}"

    try:
        spec = build_unit_pattern_spec(unit_id, pattern_id, mode=mode)
    except FileNotFoundError as e:
        return False, str(e)

    result = auto_generate_skill_code(
        skill_id,
        queue=None,
        custom_master_spec=spec,
        custom_output_path=out_path,
        ablation_id=3,
    )

    if isinstance(result, tuple):
        is_ok, msg = result[0], result[1] if len(result) > 1 else ""
    else:
        is_ok, msg = result, ""

    return is_ok, msg


def main():
    parser = argparse.ArgumentParser(
        description="產生單元 base + 題型 delta 的技能程式碼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --pattern RadicalSimplify
  python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --all
  python scripts/sync_unit_pattern_skills.py --unit jh_數學2上_FourOperationsOfRadicals --all --mode benchmark
        """,
    )
    parser.add_argument('--unit', required=True, help='單元 ID（對應 agent_skills/<unit_id>/）')
    parser.add_argument('--pattern', help='指定單一題型 ID（對應 patterns/<pattern_id>.md）')
    parser.add_argument('--all', action='store_true', help='處理該單元下所有 pattern')
    parser.add_argument('--mode', choices=['benchmark', 'liveshow'], help='可選：合併 prompt_benchmark.md 或 prompt_liveshow.md')
    parser.add_argument('--no-overwrite', action='store_true', help='若 skill 檔已存在則跳過（預設會覆寫）')
    args = parser.parse_args()

    unit_id = args.unit
    mode = args.mode

    if args.pattern:
        patterns = [args.pattern]
    elif args.all:
        patterns = list_patterns_for_unit(unit_id)
        if not patterns:
            print(f"❌ 找不到題型：{unit_id}/patterns/ 下無 .md 檔")
            sys.exit(1)
        print(f"📂 偵測到 {len(patterns)} 個 pattern: {patterns}")
    else:
        print("❌ 請指定 --pattern <id> 或 --all")
        sys.exit(1)

    app = create_app()
    skills_dir = path_in_root('skills')
    if not os.path.isdir(skills_dir):
        print(f"❌ 找不到技能目錄: {skills_dir}")
        sys.exit(1)

    with app.app_context():
        success_count = 0
        fail_count = 0
        start_time = datetime.now()

        print(f"\n🚀 開始生成 unit-pattern skills")
        print(f"   單元: {unit_id}")
        print(f"   模式 delta: {mode or '(無)'}")
        print(f"   覆寫: {'否' if args.no_overwrite else '是'}")
        print("")

        for pattern_id in tqdm(patterns, desc="Progress", unit="pattern", ncols=100):
            tqdm.write(f"  ▶ {make_pattern_skill_id(unit_id, pattern_id)}...")
            ok, msg = _generate_one(unit_id, pattern_id, mode=mode, overwrite=not args.no_overwrite)
            if ok:
                success_count += 1
                tqdm.write(f"     ✅ 成功")
            else:
                fail_count += 1
                tqdm.write(f"     ❌ {msg}")

        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 50)
        print(f"🎉 完成！")
        print(f"   成功: {success_count}")
        print(f"   失敗: {fail_count}")
        print(f"   耗時: {duration:.1f}s")
        print("=" * 50)


if __name__ == "__main__":
    main()
