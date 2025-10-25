#!/usr/bin/env python3
"""
Sanskrit Digital Library Telegram Bot
With commentary filtering like website
"""

import os
import sys
import django
import logging
from asgiref.sync import sync_to_async
from io import BytesIO

# Django setup
BACKEND_DIR = '/home/ubuntu/sanskrit-library/backend'
sys.path.insert(0, BACKEND_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_prod')
django.setup()

from django.db.models import Q
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from granthas.models import Grantha, Suggestion

# Import docx utilities
from docx import Document
from copy import deepcopy

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBSITE_URL = "https://sanskrit-digital-library.mooo.com"
ITEMS_PER_PAGE = 10

if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set!")
    sys.exit(1)


# ============================================================================
# DATABASE HELPERS
# ============================================================================

@sync_to_async
def get_grantha_count():
    return Grantha.objects.count()


@sync_to_async
def get_granthas_page(page, items_per_page):
    offset = page * items_per_page
    return list(Grantha.objects.order_by('title')[offset:offset + items_per_page])


@sync_to_async
def get_grantha_by_id(grantha_id):
    try:
        return Grantha.objects.get(id=grantha_id)
    except Grantha.DoesNotExist:
        return None


@sync_to_async
def search_granthas(search_term):
    return list(Grantha.objects.filter(
        Q(title__icontains=search_term) |
        Q(tags__icontains=search_term) |
        Q(commentaries__icontains=search_term)
    ).order_by('title')[:20])


@sync_to_async
def get_all_granthas_limited(limit=15):
    return list(Grantha.objects.order_by('title')[:limit])


@sync_to_async
def create_suggestion(grantha, user_name, user_email, suggestion_text):
    return Suggestion.objects.create(
        grantha=grantha,
        user_name=user_name,
        user_email=user_email,
        suggestion=suggestion_text,
        status='pending'
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Browse Granthas", callback_data='browse_0')],
        [InlineKeyboardButton("🔍 Search", callback_data='search')],
        [InlineKeyboardButton("💡 Submit Suggestion", callback_data='suggest_menu')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
    ])


async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass


async def edit_or_send(query, text, keyboard=None, parse_mode='Markdown'):
    try:
        await query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )
    except:
        await query.message.reply_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=parse_mode
        )


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    
    text = (
        "🙏 *Welcome to Sanskrit Digital Library!*\n\n"
        "Browse, search, and download Sanskrit texts.\n\n"
        "Choose an option below:"
    )
    
    await update.message.reply_text(
        text=text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await delete_user_message(update)
    
    text = (
        "ℹ️ *Help*\n\n"
        "*Commands:*\n"
        "/start - Main menu\n"
        "/help - This message\n\n"
        "*Features:*\n"
        "• Browse all granthas\n"
        "• Filter by commentaries\n"
        "• Search texts\n"
        "• Download filtered files\n"
        "• Submit suggestions\n\n"
        f"*Website:* {WEBSITE_URL}"
    )
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("« Main Menu", callback_data='menu')
    ]])
    
    if update.callback_query:
        await edit_or_send(update.callback_query, text, keyboard)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


# ============================================================================
# BROWSE GRANTHAS
# ============================================================================

async def browse_granthas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split('_')[1])
    total_count = await get_grantha_count()
    
    if total_count == 0:
        text = "📚 No granthas available yet."
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("« Main Menu", callback_data='menu')
        ]])
        await edit_or_send(query, text, keyboard)
        return
    
    total_pages = (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    granthas = await get_granthas_page(page, ITEMS_PER_PAGE)
    
    text = f"📚 *Granthas* (A-Z)\n\n"
    keyboard_buttons = []
    
    for grantha in granthas:
        title = grantha.title[:50] + "..." if len(grantha.title) > 50 else grantha.title
        text += f"• {grantha.title}\n"
        keyboard_buttons.append([InlineKeyboardButton(
            title,
            callback_data=f'view_{grantha.id}'
        )])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("«", callback_data=f'browse_{page-1}'))
    nav_buttons.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data='noop'))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("»", callback_data=f'browse_{page+1}'))
    
    keyboard_buttons.append(nav_buttons)
    keyboard_buttons.append([InlineKeyboardButton("« Main Menu", callback_data='menu')])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await edit_or_send(query, text, keyboard)


# ============================================================================
# VIEW GRANTHA WITH COMMENTARY FILTER
# ============================================================================

async def view_grantha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View grantha with commentary filtering"""
    query = update.callback_query
    await query.answer()
    
    grantha_id = int(query.data.split('_')[1])
    grantha = await get_grantha_by_id(grantha_id)
    
    if not grantha:
        await query.message.reply_text("Grantha not found.")
        return
    
    # Initialize selected commentaries (all selected by default)
    if f'selected_comm_{grantha_id}' not in context.user_data:
        context.user_data[f'selected_comm_{grantha_id}'] = grantha.commentaries.copy() if grantha.commentaries else []
    
    selected = context.user_data[f'selected_comm_{grantha_id}']
    
    text = f"📖 *{grantha.title}*\n\n"
    text += f"📅 {grantha.uploaded_at.strftime('%d %B %Y')}\n\n"
    
    if grantha.commentaries:
        text += "📝 *Select Commentaries:*\n"
        text += "(All selected by default)"
    
    keyboard_buttons = []
    
    # Commentary toggle buttons
    if grantha.commentaries:
        for comm in grantha.commentaries:
            check = "✓" if comm in selected else "○"
            keyboard_buttons.append([InlineKeyboardButton(
                f"{check} {comm}",
                callback_data=f'toggle_{grantha_id}_{grantha.commentaries.index(comm)}'
            )])
    
    # Action buttons
    keyboard_buttons.append([
        InlineKeyboardButton("📥 Download", callback_data=f'download_{grantha_id}'),
        InlineKeyboardButton("💡 Suggest", callback_data=f'suggest_for_{grantha_id}')
    ])
    keyboard_buttons.append([InlineKeyboardButton("« Back", callback_data='browse_0')])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await edit_or_send(query, text, keyboard)


async def toggle_commentary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle commentary selection"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    grantha_id = int(parts[1])
    comm_index = int(parts[2])
    
    grantha = await get_grantha_by_id(grantha_id)
    
    if not grantha:
        return
    
    # Initialize if not exists
    if f'selected_comm_{grantha_id}' not in context.user_data:
        context.user_data[f'selected_comm_{grantha_id}'] = grantha.commentaries.copy()
    
    selected = context.user_data[f'selected_comm_{grantha_id}']
    commentary = grantha.commentaries[comm_index]
    
    # Toggle
    if commentary in selected:
        selected.remove(commentary)
    else:
        selected.append(commentary)
    
    # Update view
    text = f"📖 *{grantha.title}*\n\n"
    text += f"📅 {grantha.uploaded_at.strftime('%d %B %Y')}\n\n"
    text += "📝 *Select Commentaries:*\n"
    text += f"({len(selected)}/{len(grantha.commentaries)} selected)"
    
    keyboard_buttons = []
    
    for comm in grantha.commentaries:
        check = "✓" if comm in selected else "○"
        keyboard_buttons.append([InlineKeyboardButton(
            f"{check} {comm}",
            callback_data=f'toggle_{grantha_id}_{grantha.commentaries.index(comm)}'
        )])
    
    keyboard_buttons.append([
        InlineKeyboardButton("📥 Download", callback_data=f'download_{grantha_id}'),
        InlineKeyboardButton("💡 Suggest", callback_data=f'suggest_for_{grantha_id}')
    ])
    keyboard_buttons.append([InlineKeyboardButton("« Back", callback_data='browse_0')])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    await edit_or_send(query, text, keyboard)


# ============================================================================
# DOWNLOAD WITH FILTERING
# ============================================================================

async def download_grantha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download filtered grantha file"""
    query = update.callback_query
    await query.answer("Preparing download...")
    
    grantha_id = int(query.data.split('_')[1])
    grantha = await get_grantha_by_id(grantha_id)
    
    if not grantha:
        await query.answer("Grantha not found", show_alert=True)
        return
    
    try:
        if not grantha.file or not os.path.exists(grantha.file.path):
            await query.answer("File not available", show_alert=True)
            return
        
        # Get selected commentaries
        selected_comm = context.user_data.get(f'selected_comm_{grantha_id}', grantha.commentaries or [])
        
        # If all commentaries selected or no commentaries, send original file
        if not grantha.commentaries or set(selected_comm) == set(grantha.commentaries):
            with open(grantha.file.path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"{grantha.title}.docx",
                    caption=f"📖 {grantha.title}"
                )
        else:
            # Filter document
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            # Helper function for filtering (synchronous)
            def filter_sync():
                from granthas.utils import filter_docx_by_commentaries
                
                selected_data = {
                    'all_commentaries': grantha.commentaries,
                    'selected': selected_comm
                }
                
                return filter_docx_by_commentaries(grantha.file.path, selected_data)
            
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                filtered_buffer = await loop.run_in_executor(executor, filter_sync)
            
            # Send filtered file
            filtered_buffer.seek(0)
            await query.message.reply_document(
                document=filtered_buffer,
                filename=f"{grantha.title}_filtered.docx",
                caption=f"📖 {grantha.title}\n\n✓ Filtered: {', '.join(selected_comm) if selected_comm else 'None'}"
            )
            
    except Exception as e:
        logger.error(f"Download error: {e}", exc_info=True)
        await query.answer("Error downloading file", show_alert=True)


# ============================================================================
# SEARCH
# ============================================================================

async def search_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "🔍 *Search*\n\nEnter search term:"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Cancel", callback_data='menu')]])
    
    await edit_or_send(query, text, keyboard)
    context.user_data['awaiting_search'] = True


async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_search'):
        return
    
    search_term = update.message.text.strip()
    await delete_user_message(update)
    
    context.user_data['awaiting_search'] = False
    granthas = await search_granthas(search_term)
    
    if not granthas:
        text = f"🔍 No results for '{search_term}'"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Main Menu", callback_data='menu')]])
    else:
        text = f"🔍 *Results for '{search_term}':*\n\n"
        buttons = []
        
        for g in granthas:
            title = g.title[:50] + "..." if len(g.title) > 50 else g.title
            text += f"• {g.title}\n"
            buttons.append([InlineKeyboardButton(title, callback_data=f'view_{g.id}')])
        
        buttons.append([InlineKeyboardButton("🔍 New Search", callback_data='search')])
        buttons.append([InlineKeyboardButton("« Main Menu", callback_data='menu')])
        keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


# ============================================================================
# SUGGESTIONS
# ============================================================================

async def suggest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = "💡 *Submit Suggestion*\n\nChoose a grantha:"
    granthas = await get_all_granthas_limited(15)
    buttons = []
    
    for g in granthas:
        title = g.title[:50] + "..." if len(g.title) > 50 else g.title
        buttons.append([InlineKeyboardButton(title, callback_data=f'suggest_for_{g.id}')])
    
    buttons.append([InlineKeyboardButton("« Main Menu", callback_data='menu')])
    keyboard = InlineKeyboardMarkup(buttons)
    
    await edit_or_send(query, text, keyboard)


async def suggest_for_grantha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    grantha_id = int(query.data.split('_')[2])
    grantha = await get_grantha_by_id(grantha_id)
    
    if not grantha:
        await query.answer("Grantha not found", show_alert=True)
        return
    
    context.user_data['suggest_grantha_id'] = grantha_id
    context.user_data['awaiting_suggestion'] = True
    
    text = f"💡 *Suggestion for:*\n{grantha.title}\n\nType your suggestion:"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Cancel", callback_data='menu')]])
    
    await edit_or_send(query, text, keyboard)


async def handle_suggestion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('awaiting_suggestion'):
        return
    
    suggestion_text = update.message.text.strip()
    grantha_id = context.user_data.get('suggest_grantha_id')
    
    await delete_user_message(update)
    context.user_data['awaiting_suggestion'] = False
    
    try:
        grantha = await get_grantha_by_id(grantha_id)
        
        if not grantha:
            await update.message.reply_text("Error: Grantha not found.")
            return
        
        await create_suggestion(
            grantha,
            f"{update.effective_user.first_name} (Telegram)",
            f"tg_{update.effective_user.id}@telegram.user",
            suggestion_text
        )
        
        text = "✅ *Suggestion submitted!*\n\nThank you for your feedback."
        keyboard = get_main_menu_keyboard()
        
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        await update.message.reply_text("Error submitting suggestion.")


# ============================================================================
# CALLBACK ROUTER
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == 'menu':
        text = "🙏 *Sanskrit Digital Library*\n\nChoose an option:"
        await edit_or_send(query, text, get_main_menu_keyboard())
        await query.answer()
        
    elif data.startswith('browse_'):
        await browse_granthas(update, context)
        
    elif data.startswith('view_'):
        await view_grantha(update, context)
        
    elif data.startswith('toggle_'):
        await toggle_commentary(update, context)
        
    elif data.startswith('download_'):
        await download_grantha(update, context)
        
    elif data == 'search':
        await search_prompt(update, context)
        
    elif data == 'suggest_menu':
        await suggest_menu(update, context)
        
    elif data.startswith('suggest_for_'):
        await suggest_for_grantha(update, context)
        
    elif data == 'help':
        await help_command(update, context)
        
    elif data == 'noop':
        await query.answer()
    else:
        await query.answer()


# ============================================================================
# MESSAGE HANDLER
# ============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_search'):
        await handle_search(update, context)
    elif context.user_data.get('awaiting_suggestion'):
        await handle_suggestion(update, context)
    else:
        await delete_user_message(update)
        await update.message.reply_text("Use /start for main menu")


# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)


# ============================================================================
# MAIN
# ============================================================================

def main():
    import asyncio
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)
    
    logger.info("Bot started with commentary filtering!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
