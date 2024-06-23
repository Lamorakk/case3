import aiomysql
from config import DB_CONFIG

async def get_pool():
    return await aiomysql.create_pool(
        host=DB_CONFIG['host'],
        port=3306,
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        db=DB_CONFIG['database'],
        autocommit=True
    )

async def get_user(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            return await cur.fetchone()

async def create_user(pool, user_id, user_name, referrer_id=None):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO users (user_id, user_name, referrer_id) VALUES (%s, %s, %s)", (user_id, user_name, referrer_id))

async def update_balance(pool, user_id, amount):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))


async def update_balance(pool, user_id, amount):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE users SET balance = balance + %s WHERE user_id = %s", (amount, user_id))

async def create_withdrawal_request(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO withdrawal_requests (user_id) VALUES (%s)", (user_id,))
            return cur.lastrowid

async def get_pending_request(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM withdrawal_requests WHERE user_id = %s AND status = 'pending'", (user_id,))
            return await cur.fetchone()

# New functions for user access
async def check_user_access(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT access_granted FROM user_access WHERE user_id = %s", (user_id,))
            return await cur.fetchone()

async def set_user_access(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO user_access (user_id, access_granted) VALUES (%s, TRUE) ON DUPLICATE KEY UPDATE access_granted = TRUE")
async def get_pending_orders(pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM withdrawal_requests WHERE status = 'pending'")
            return await cur.fetchall()

async def update_order_status(pool, order_id, status):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE withdrawal_requests SET status = %s WHERE request_id = %s", (status, order_id))