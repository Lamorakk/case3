from aiogram import Bot
from database import get_pool, get_user

import os
import networkx as nx
import matplotlib.pyplot as plt
from aiogram.types import FSInputFile
import pygraphviz as pgv

async def create_vertical_referral_tree_image(user_id, referral_data):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    def add_edges(node, parent=None):
        G.add_node(node["name"])
        if parent:
            G.add_edge(parent, node["name"])
        for child in node.get("children", []):
            add_edges(child, node["name"])

    # The inviter will be the root node, so we need to add the user's parent first
    inviter = {"name": "Inviter", "children": [referral_data]}
    add_edges(inviter)

    # Draw the graph using Graphviz layout
    pos = nx.nx_agraph.graphviz_layout(G, prog='dot')

    # Draw the graph
    plt.figure(figsize=(10, 15))
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True, arrowstyle="->", arrowsize=20)

    # Save the image
    image_path = f"C:\\Users\\medok\\PycharmProjects\\case3\\media\\referral_tree_{user_id}.png"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    plt.savefig(image_path)
    plt.close()

    return image_path

async def send_referral_tree_image(bot: Bot, user_id: int):
    async with await get_pool() as pool:
        # Get referral data from the database
        referral_tree_data = await get_referral_tree_data(pool, user_id)

        if referral_tree_data:
            image_path = await create_vertical_referral_tree_image(user_id, referral_tree_data)

            # Send the image to the user
            photo = FSInputFile(image_path)
            await bot.send_photo(user_id, photo)

            # Clean up old image file
            await delete_old_referral_tree_image(pool, user_id)
            await save_referral_tree_image(pool, user_id, image_path)

# Helper functions to interact with the database
async def get_referral_tree_data(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = await cur.fetchone()
            if not user:
                return None
            return await build_tree(pool, user_id)

async def build_tree(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT user_id, user_name FROM users WHERE user_id = %s", (user_id,))
            user = await cur.fetchone()
            tree = {"id": user[0], "name": user[1], "children": []}
            await cur.execute("SELECT user_id FROM users WHERE referrer_id = %s", (user_id,))
            referrals = await cur.fetchall()
            for referral in referrals:
                child_tree = await build_tree(pool, referral[0])
                tree["children"].append(child_tree)
            return tree

async def delete_old_referral_tree_image(pool, user_id):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT image_path FROM referral_trees WHERE user_id = %s", (user_id,))
            result = await cur.fetchone()
            if result:
                image_path = result[0]
                if os.path.exists(image_path):
                    os.remove(image_path)
                await cur.execute("DELETE FROM referral_trees WHERE user_id = %s", (user_id,))

async def save_referral_tree_image(pool, user_id, image_path):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO referral_trees (user_id, image_path) VALUES (%s, %s)",
                              (user_id, image_path))
