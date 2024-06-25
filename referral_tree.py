from aiogram import Bot
from database import get_pool, get_user

import os
import networkx as nx
from PIL import Image, ImageDraw, ImageFont
from aiogram.types import FSInputFile


async def create_vertical_referral_tree_image(user_id, referral_data):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes and edges
    def add_edges(node, parent=None):
        G.add_node(node["name"], label=node["name"], color="blue")
        if parent:
            G.add_edge(parent, node["name"], color="red")
        for child in node.get("children", []):
            add_edges(child, node["name"])

    # The inviter will be the root node, so we need to add the user's parent first
    inviter = {"name": "Inviter", "children": [referral_data]}
    add_edges(inviter)

    # Create a custom layout to position nodes vertically
    def vertical_layout(G):
        pos = {}
        layer = 0
        nodes = list(nx.topological_sort(G))
        for node in nodes:
            pos[node] = (0, -layer * 100)
            layer += 1
        return pos

    pos = vertical_layout(G)

    # Draw the graph with PIL
    node_size = 50
    image_width = 800
    image_height = len(G.nodes) * 100 + 100
    img = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(img)

    # Define cold colors for nodes
    tier_colors = {
        0: "purple",
        1: "blue",
        2: "lightblue",
        3: "lightgreen",
        4: "cyan"
    }

    # Draw edges
    for edge in G.edges(data=True):
        start_pos = pos[edge[0]]
        end_pos = pos[edge[1]]
        draw.line((start_pos[0] + image_width // 2, start_pos[1] + 50, end_pos[0] + image_width // 2, end_pos[1] + 50),
                  fill="red", width=3)

    # Draw nodes
    font = ImageFont.truetype("arial.ttf", 14)
    node_tiers = nx.shortest_path_length(G, source="Inviter")
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        x = x + image_width // 2
        y = y + 50
        tier = node_tiers[node[0]]
        color = tier_colors.get(tier, "grey")

        # Draw the node as a circle
        draw.ellipse((x - node_size / 2, y - node_size / 2, x + node_size / 2, y + node_size / 2), fill=color,
                     outline="black", width=2)

        # Draw the label
        text_bbox = draw.textbbox((0, 0), node[0], font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((x - text_width / 2, y - text_height / 2), node[0], fill="black", font=font)

    # Save the image
    image_path = f"C:\\Users\\medok\\PycharmProjects\\case3\\media\\referral_tree_{user_id}.png"
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    img.save(image_path)

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
            await cur.execute("INSERT INTO referral_trees (user_id, image_path) VALUES (%s, %s)", (user_id, image_path))
