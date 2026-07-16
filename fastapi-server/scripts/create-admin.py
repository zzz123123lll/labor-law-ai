#!/usr/bin/env python3
"""创建管理员账号脚本。

用法:
    python scripts/create-admin.py

    或在命令行指定 openid:
    python scripts/create-admin.py --openid=your-wechat-openid

管理后台地址: http://localhost:3000/admin  (需先启动 admin-panel)
管理 API 需要 JWT token，脚本创建完成后会打印 token。
"""
import asyncio
import uuid
import os
import sys
import argparse

# Windows console encoding fix
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

from app.database import AsyncSessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.utils.security import create_access_token, create_refresh_token


async def create_admin(openid: str | None = None, phone: str | None = None):
    # 确保表存在
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        if openid:
            existing = await db.execute(
                select(User).where(User.wechat_openid == openid)
            )
            user = existing.scalar_one_or_none()
            if user:
                user.role = "admin"
                await db.commit()
                print(f"[OK] 已有用户已升级为管理员: openid={openid}, id={user.id}")
            else:
                user = User(
                    id=uuid.uuid4(),
                    wechat_openid=openid,
                    role="admin",
                    nickname=phone or "管理员",
                    phone=phone,
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"[OK] 管理员账号已创建: openid={openid}, id={user.id}")
        else:
            # 没有指定 openid 时，用任意一个已有的用户，或创建新的
            existing_result = await db.execute(select(User).limit(1))
            user = existing_result.scalar_one_or_none()

            if user:
                user.role = "admin"
                await db.commit()
                print(f"[OK] 第一个用户已升级为管理员: id={user.id}, openid={user.wechat_openid}")
            else:
                user = User(
                    id=uuid.uuid4(),
                    wechat_openid=f"admin-{uuid.uuid4().hex[:8]}",
                    role="admin",
                    nickname="管理员",
                )
                db.add(user)
                await db.commit()
                await db.refresh(user)
                print(f"[OK] 新管理员账号已创建: id={user.id}")

        print()
        print("=" * 60)
        print("管理员 JWT Token（用于 API 测试）:")
        print(f"  access_token:  {create_access_token(str(user.id))}")
        print(f"  refresh_token: {create_refresh_token(str(user.id))}")
        print()
        print("管理后台使用:")
        print(f"  后端启动:  uvicorn app.main:app --reload")
        print(f"  后台启动:  cd admin-panel && npm run dev")
        print(f"  admin 后端: http://localhost:8000/docs")
        print()
        print("📌 在不连接的 openid 的情况下，上面这条 token 可以用于 API 调用来做管理员操作。")
        print("📌 管理员用户 openid: ", user.wechat_openid)
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="创建管理员账号")
    parser.add_argument("--openid", help="微信 openid（可选，未提供则使用第一个已有用户）")
    parser.add_argument("--phone", help="手机号（可选）")
    args = parser.parse_args()

    asyncio.run(create_admin(args.openid, args.phone))


if __name__ == "__main__":
    main()
