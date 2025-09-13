# bot_mines.py
import time
import random
import logging
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler

# ========== CONFIG ==========
TOKEN = "8272197234:AAHpVytSM3IAkjvcuQp6nyN9gKiolKLu3t4"           # <-- Mets ici ton nouveau token (NE PAS le partager)
TON_ID_ADMIN = 7530082416         # <-- Ton ID Telegram (admin)
INSCRIPTION_LINK = "https://1wlucb.life/v3/aggressive-casino?p=naub"
CANAL_LINK = "https://t.me/+neQ37IL3AiEzOTBk"
CONTACT_TELEGRAM = "https://t.me/amour20251"  # lien pour "Achetez"

# ========== LOGGING ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== DONNÉES EN MÉMOIRE ==========
# Structure users[user_id] = {
#   "status": "bloque" | "actif",
#   "pred_left": int,
#   "last_prediction_ts": float (epoch secs) or 0,
#   "last_message_id": int or None
# }
users = {}

# ========== UTIL ==========

def ensure_user(uid):
    if uid not in users:
        users[uid] = {"status": "bloque", "pred_left": 20, "last_prediction_ts": 0, "last_message_id": None}

def make_start_message():
    text = (
        "<b>Gagne de l'argent sur BombMaker 1WIN</b>\n\n"
        "Grâce à la nouvelle version de ChatGPT qui analyse le jeu, ce bot te propose des signaux Mines.\n\n"
        "🔹 Rapide\n🔹 Automatisé\n🔹 Facile à utiliser\n\n"
        "Appuie sur <b>Commence</b> pour voir les instructions et t'inscrire."
    )
    keyboard = [[InlineKeyboardButton("Commence", callback_data="commence")]]
    return text, InlineKeyboardMarkup(keyboard)

def make_1win_message():
    text = (
        "COMMENT AVOIR UN COMPTE 1WIN🇮🇹 AUTHENTIQUE:.. 🆙\n\n"
        "GUIDE EN IMAGE ….‼️‼️\n"
        "✍️✍️✍️✍️✍️\n"
        "Pour gagner gros il faut avoir un compte professionnel et un algorithme très bas et pour cela je te conseille le code promo👇\n"
        "Code promo➡️ VVIP250 ⭐️ \n\n"
        "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣\n"
        "Recharge toi gros afin que tu puisses gagner minimum 50.000F à 100.000F par jours ✍️\n\n"
        f"🇮🇹Lien d’inscription 🔛 {INSCRIPTION_LINK}\n\n"
        "👉 Maintenant, envoie-moi ton ID de compte 1WIN."
    )
    keyboard = [
        [InlineKeyboardButton("Inscription", url=INSCRIPTION_LINK)],
        [InlineKeyboardButton("Vérifier (envoyer ID)", callback_data="ask_id")],
    ]
    return text, InlineKeyboardMarkup(keyboard)

# ========== HANDLERS ==========

def start_cmd(update: Update, context: CallbackContext):
    user = update.effective_user
    ensure_user(user.id)
    text, markup = make_start_message()
    update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    uid = query.from_user.id

    if data == "commence":
        # envoyer le message 1WIN avec boutons
        text, markup = make_1win_message()
        query.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)
    elif data == "ask_id":
        # demander à l'utilisateur d'envoyer son ID 1WIN (texte)
        context.bot.send_message(chat_id=uid, text="📝 Envoie-moi maintenant ton ID 1WIN (texte). Si tu veux, précise aussi combien d'amis tu as invités.")
    elif data.startswith("admin_validate_"):
        # admin clique sur Valider d'une notification
        parts = data.split("_")
        if len(parts) >= 3:
            target_id = int(parts[2])
            if query.from_user.id != TON_ID_ADMIN:
                query.message.reply_text("🚫 Tu n'es pas admin.")
                return
            # valider
            ensure_user(target_id)
            users[target_id]["status"] = "actif"
            users[target_id]["pred_left"] = 20
            context.bot.send_message(chat_id=target_id, text="✅ Ton compte a été validé par l'admin. Tu peux utiliser /prediction ou appuyer sur Prochaine cote.")
            query.message.reply_text(f"✅ Utilisateur {target_id} validé.")
    elif data.startswith("admin_refuse_"):
        parts = data.split("_")
        target_id = int(parts[2])
        if query.from_user.id != TON_ID_ADMIN:
            query.message.reply_text("🚫 Tu n'es pas admin.")
            return
        # refuser
        context.bot.send_message(chat_id=target_id, text="❌ Ta demande a été refusée par l'admin.")
        query.message.reply_text(f"❌ Utilisateur {target_id} refusé.")
    elif data.startswith("admin_confirm_buy_"):
        parts = data.split("_")
        target_id = int(parts[3])
        if query.from_user.id != TON_ID_ADMIN:
            query.message.reply_text("🚫 Tu n'es pas admin.")
            return
        # accorder par exemple 20 prédictions supplémentaires
        ensure_user(target_id)
        users[target_id]["pred_left"] += 20
        context.bot.send_message(chat_id=target_id, text="✅ Achat confirmé par l'admin — 20 prédictions ajoutées à ton compte.")
        query.message.reply_text(f"✅ Achat confirmé pour {target_id}, 20 signaux ajoutés.")

def handle_text(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    text = update.message.text.strip()

    # commande texte "Prochaine cote" ou "cote" déclenche prediction
    if text.lower().find("prochaine cote") != -1 or text.lower().find("cote") != -1:
        return prediction_cmd(update, context)

    # si utilisateur dit "j'ai invité" -> notifier admin (user peut préciser nb d'amis)
    if "jai invite" in text.lower() or "j'ai invité" in text.lower() or "j ai invité" in text.lower():
        # envoyer message admin avec boutons valider/refuser
        ensure_user(uid)
        # on permet à l'utilisateur d'ajouter un nombre dans le même texte (ex: "j'ai invité 2")
        invited_count = None
        for word in text.split():
            if word.isdigit():
                invited_count = int(word)
                break
        msg = f"📩 L'utilisateur {uid} dit avoir invité {invited_count if invited_count else 'des amis'}. \nID: {uid}\nTape /valider {uid} pour valider ou utilise les boutons ci-dessous."
        keyboard = [
            [
                InlineKeyboardButton("Valider", callback_data=f"admin_validate_{uid}"),
                InlineKeyboardButton("Refuser", callback_data=f"admin_refuse_{uid}")
            ]
        ]
        context.bot.send_message(chat_id=TON_ID_ADMIN, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text("✅ Message envoyé à l'admin. Attends la validation.")
        return

    # Si c'est un ID (on suppose que l'utilisateur a envoyé son ID 1WIN après avoir cliqué Vérifier)
    # heuristique: si le message contient uniquement chiffres ou alphanum et longueur raisonnable => on l'accepte comme ID
    if text and len(text) <= 60:
        # enregistrer comme id_1win et prévenir admin
        ensure_user(uid)
        users[uid]["id_1win"] = text
        # notifier admin avec bouton valider
        msg = f"📩 Nouvel envoi d'ID 1WIN:\nUser: {uid}\nID 1WIN: {text}\n\nValide si ok."
        keyboard = [
            [
                InlineKeyboardButton("Valider", callback_data=f"admin_validate_{uid}"),
                InlineKeyboardButton("Refuser", callback_data=f"admin_refuse_{uid}")
            ]
        ]
        context.bot.send_message(chat_id=TON_ID_ADMIN, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        update.message.reply_text("✅ Merci, ton ID a été reçu. Je vais le signaler à l'admin pour validation.")
        # envoyer instruction invite canal et lien d'invite (user devra inviter, admin valide manuellement)
        invite_link = f"https://t.me/{context.bot.username}?start={uid}"
        update.message.reply_text(
            f"👉 Maintenant, rejoins le canal {CANAL_LINK} et invite 3 amis via ce lien :\n{invite_link}\n\n"
            "⚠️ Tant que l'admin ne valide pas, ton accès restera bloqué."
        )
        return

    # sinon : message neutre -> répondre
    update.message.reply_text("Je n'ai pas compris. Utilise /start ou clique sur les boutons proposés.")

# ====== PREDICTION LOGIC ======
def prediction_cmd(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    ensure_user(uid)
    user = users[uid]

    if user["status"] != "actif":
        update.message.reply_text("⚠️ Ton accès est bloqué. Attends que l'admin te valide.")
        return

    now = time.time()
    # comportement demandé :
    # - 3 minutes cooldown between predictions
    # - if press again in same minute (i.e. within 60s after last request), send "Prédiction en cours d'analyse..."
    last = user.get("last_prediction_ts", 0)
    elapsed = now - last

    if elapsed < 60:
        # within same minute -> "en cours d'analyse"
        update.message.reply_text("⏳ Prédiction en cours d'analyse... Attends quelques secondes.")
        return
    if elapsed < 180:
        # if between 60s and 3min -> tell to wait remaining
        remaining = int(180 - elapsed)
        update.message.reply_text(f"⏳ Please wait {remaining} secondes avant la prochaine prédiction.")
        return

    if user.get("pred_left", 0) <= 0:
        # plus de prédictions: proposer achat
        keyboard = [
            [InlineKeyboardButton("Achetez", url=CONTACT_TELEGRAM)],
            [InlineKeyboardButton("Vérifier l'achat", callback_data=f"verify_buy_{uid}")]
        ]
        update.message.reply_text(
            "❌ Ton volume de prédictions est terminé. Veux-tu acheter des signaux ?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # supprimer ancien message prédiction s'il existe
    if user.get("last_message_id"):
        try:
            context.bot.delete_message(chat_id=uid, message_id=user["last_message_id"])
        except:
            pass

    # Générer une prédiction: 5 étoiles dans chaque prédiction, positions aléatoires (ici 5 étoiles)
    board = [["🟦" for _ in range(5)] for _ in range(5)]
    stars = random.sample([(i, j) for i in range(5) for j in range(5)], 5)
    for (i, j) in stars:
        board[i][j] = "⭐️"
    text_grid = "\n".join("".join(row) for row in board)
    message_text = f"<b>🎯 Nouvelle prédiction</b>\n\n{text_grid}\n\n➡️ Mets les pièges sur <b>3</b> !\n\n<b>Prédictions restantes:</b> {user['pred_left']-1}"
    sent = update.message.reply_text(message_text, parse_mode=ParseMode.HTML)

    # mettre à jour user
    user["last_message_id"] = sent.message_id
    user["last_prediction_ts"] = now
    user["pred_left"] -= 1

# ====== CALLBACK pour verify buy (lorsque user clique 'Vérifier l'achat') ======
def callback_verify_buy(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data
    uid = query.from_user.id

    if data.startswith("verify_buy_"):
        # notifier admin: vérifier que l'achat a été effectué pour user
        parts = data.split("_")
        target = int(parts[2])
        msg = f"📩 L'utilisateur {target} dit avoir acheté des signaux. Confirmer l'achat ?"
        kb = [
            [InlineKeyboardButton("Valide achat (+20)", callback_data=f"admin_confirm_buy_{target}")],
            [InlineKeyboardButton("Refuser", callback_data=f"admin_refuse_{target}")]
        ]
        context.bot.send_message(chat_id=TON_ID_ADMIN, text=msg, reply_markup=InlineKeyboardMarkup(kb))
        query.message.reply_text("✅ Demande envoyée à l'admin pour vérification de l'achat.")

# ====== ADMIN COMMANDS ======
def cmd_valider(update: Update, context: CallbackContext):
    if update.effective_user.id != TON_ID_ADMIN:
        update.message.reply_text("🚫 Tu n'es pas admin.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /valider <user_id>")
        return
    try:
        target = int(context.args[0])
        ensure_user(target)
        users[target]["status"] = "actif"
        users[target]["pred_left"] = 20
        context.bot.send_message(chat_id=target, text="✅ Ton compte a été validé par l'admin. Tu peux utiliser /prediction.")
        update.message.reply_text(f"✅ {target} validé.")
    except Exception as e:
        update.message.reply_text("Erreur: impossible de valider.")

def cmd_refuser(update: Update, context: CallbackContext):
    if update.effective_user.id != TON_ID_ADMIN:
        update.message.reply_text("🚫 Tu n'es pas admin.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /refuser <user_id>")
        return
    try:
        target = int(context.args[0])
        if target in users:
            users[target]["status"] = "bloque"
        context.bot.send_message(chat_id=target, text="❌ Ta demande a été refusée par l'admin.")
        update.message.reply_text(f"❌ {target} refusé.")
    except:
        update.message.reply_text("Erreur: impossible de refuser.")

def cmd_liste(update: Update, context: CallbackContext):
    if update.effective_user.id != TON_ID_ADMIN:
        update.message.reply_text("🚫 Tu n'es pas admin.")
        return
    msg = "📋 Liste utilisateurs\n"
    for uid, u in users.items():
        msg += f"ID:{uid} | statut:{u['status']} | pred_left:{u['pred_left']}\n"
    update.message.reply_text(msg or "Aucun utilisateur.")

# ===== MAIN =====
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CallbackQueryHandler(button_callback))            # boutons Commence / ask_id / admin validate/refuse / admin confirm buy
    dp.add_handler(CommandHandler("prediction", prediction_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # admin commands
    dp.add_handler(CommandHandler("valider", cmd_valider))
    dp.add_handler(CommandHandler("refuser", cmd_refuser))
    dp.add_handler(CommandHandler("liste", cmd_liste))

    # callback specific verify buy
    dp.add_handler(CallbackQueryHandler(callback_verify_buy, pattern=r"^verify_buy_"))

    updater.start_polling()
    logger.info("Bot démarré")
    updater.idle()

if __name__ == "__main__":
    main()
