# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

_base = Path(SPECPATH)

a = Analysis(
    ['run.py'],
    pathex=[str(_base)],
    binaries=[],
    datas=[
        # 法律数据
        ('app/legal_engine/data/laws/*.yaml', 'legal_engine/data/laws'),
        # 案例数据通过 case_store.py 加载，无独立 YAML 目录
        ('app/legal_engine/data/precedents/index.json', 'legal_engine/data/precedents'),
        # 仲裁委数据
        ('app/legal_engine/data/arbitration_committees.json', 'legal_engine/data'),
        # 前端静态文件
        ('../web-app/out', 'frontend'),
        # .env.example 作为默认配置参考
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'app', 'app.main', 'app.config', 'app.database', 'app.errors', 'app.logging_config',
        'app.models', 'app.models.base', 'app.models.user', 'app.models.case',
        'app.models.message', 'app.models.evidence', 'app.models.contract_review',
        'app.models.compensation', 'app.models.document', 'app.models.subscription',
        'app.models.order',
        'app.api', 'app.api.deps', 'app.api.cases', 'app.api.consultation',
        'app.api.contract_review', 'app.api.evidence', 'app.api.compensation',
        'app.api.document_gen', 'app.api.payment', 'app.api.admin', 'app.api.settings',
        'app.ai', 'app.ai.base', 'app.ai.deepseek', 'app.ai.adapters',
        'app.agents', 'app.agents.base', 'app.agents.router', 'app.agents.registry',
        'app.agents.case_analysis', 'app.agents.violation_detect', 'app.agents.compensation_calc',
        'app.agents.contract_review', 'app.agents.evidence_analyze', 'app.agents.document_draft',
        'app.agents.arbitration_guide', 'app.agents.strategy_plan', 'app.agents.evidence_checklist',
        'app.api.arbitration',
        'app.legal_engine', 'app.legal_engine.law_store', 'app.legal_engine.case_store',
        'app.schemas', 'app.schemas.auth', 'app.schemas.case', 'app.schemas.consultation',
        'app.schemas.contract', 'app.schemas.evidence', 'app.schemas.compensation',
        'app.schemas.document', 'app.schemas.payment', 'app.schemas.admin',
        'app.utils', 'app.utils.security',
        # 第三方依赖
        'yaml', 'jinja2', 'httpx', 'slowapi', 'aiofiles', 'aiosqlite',
        'passlib', 'jose', 'pydantic', 'pydantic_settings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'paddleocr', 'paddlepaddle', 'paddle',
        'redis', 'asyncpg', 'celery', 'kafka',
        'matplotlib', 'numpy', 'scipy', 'pandas', 'cv2', 'PIL',
        'tkinter', 'PyQt5', 'wx',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='劳动法AI维权助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口（服务日志）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如有 icon.ico 放项目根目录
)
