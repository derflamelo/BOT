import random
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from collections import defaultdict

# === CONFIGURATION ===
TOKEN = "8272197234:AAHpVytSM3IAkjvcuQp6nyN9gKiolKLu3t4"
CANAL_ID = "@derflamelo25"

# === BASE DE DONNÉES SIMPLE ===
user_state = {}               # État de chaque utilisateur (WAIT_ID, VALIDATED, UNLOCKED)
referrals = defaultdict(list) # Qui a invité qui (id_parent -> [id_filleuls])

# === LISTE DE PREDICTIONS ===
predictions = [
    "🎯 Prédiction MINES 1WIN :\n\nMines: 3\n\n🟦🟦🟦🟦🟦\n🟦🟦⭐️🟦🟦\n⭐️🟦🟦🟦🟦\n🟦🟦🟦🟦⭐️\n🟦🟦🟦🟦🟦\n\n👉 Mets sur piège 3 !",

    "🎯 Prédiction MINES 1WIN :\n\nMines: 2\n\n⭐️🟦🟦🟦🟦\n🟦🟦🟦🟦⭐️\n🟦⭐️🟦🟦🟦\n🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n\n👉 Mets sur piège 2 !",

    "🎯 Prédiction MINES 1WIN :\n\nMines: 4\n\n🟦🟦⭐️🟦🟦\n🟦⭐️🟦🟦🟦\n🟦🟦🟦⭐️🟦\n⭐️🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n\n👉 Mets sur piège 4 !",

    "🎯 Prédiction MINES 1WIN :\n\nMines: 5\n\n🟦⭐️🟦🟦⭐️\n🟦🟦🟦⭐️🟦\n⭐️🟦🟦🟦🟦\n🟦🟦⭐️🟦🟦\n🟦🟦🟦🟦🟦\n\n👉 Mets sur piège 5 !",

    "🎯 Prédiction MINES 1WIN :\n\nMines: 1\n\n⭐️🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n🟦🟦🟦🟦🟦\n\n👉 Mets sur piège 1 !"
]


# === FONCTIONS ===
def start(update, context):
    user_id = update.message.chat_id
    args = context.args  # Si l’utilisateur a été invité

    # Si l’utilisateur est invité par quelqu’un
    if args:
        parrain_id = int(args[0])
        if user_id not in referrals[parrain_id]:
            referrals[parrain_id].append(user_id)
            context.bot.send_message(
                chat_id=parrain_id,
                text=f"🎉 Ton ami {update.message.from_user.first_name} a rejoint via ton lien !"
            )
            # Vérifier si le parrain a 3 amis
            if len(referrals[parrain_id]) >= 3 and user_state.get(parrain_id) == "VALIDATED":
                user_state[parrain_id] = "UNLOCKED"
                context.bot.send_message(
                    chat_id=parrain_id,
                    text="✅ Bravo ! Tu as invité 3 amis, ton accès aux prédictions est débloqué 🎯"
                )

    # Message d’accueil
    user_state[user_id] = "WAIT_ID"
    message = (
        "COMMENT AVOIR UN COMPTE 1WIN🇮🇹 AUTHENTIQUE:.. 🆙\n\n"
        "GUIDE EN IMAGE ….‼️‼️\n"
        "✍️✍️✍️✍️✍️\n"
        "Pour gagner gros il faut avoir un compte professionnel et un algorithme très bas "
        "et pour cela je te conseille le code promo👇\n"
        "Code promo➡️ Mine11 ⭐️\n\n"
        "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣\n"
        "Recharge toi gros afin que tu puisses gagner minimum 50.000F à 100.000F par jours ✍️\n\n"
        "🇮🇹Lien d’inscription 🔛 https://1wlevw.life/casino/list/4?p=e97v\n\n"
        "👉 Maintenant, envoie-moi ton ID de compte 1WIN."
    )
    update.message.reply_text(message)


def handle_message(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    # Étape 1 : Attente ID 1WIN
    if user_state.get(user_id) == "WAIT_ID":
        update.message.reply_text("✅ Merci, ton ID a été reçu. Je vais le valider.")
        user_state[user_id] = "VALIDATED"

        # Donne un lien d’invitation personnalisé
        invite_link = f"https://t.me/{context.bot.username}?start={user_id}"
        update.message.reply_text(
            f"👉 Maintenant, rejoins le canal {CANAL_ID} et invite 3 amis via ce lien :\n{invite_link}\n\n"
            "⚠️ Tant que 3 amis n’ont pas rejoint, ton accès restera bloqué."
        )

    # Étape 2 : Attente d’invitations
    elif user_state.get(user_id) == "VALIDATED":
        update.message.reply_text("⚠️ Tu dois encore inviter 3 amis avec ton lien pour débloquer l’accès.")

    else:
        update.message.reply_text("❌ Utilise la commande /start pour commencer.")


def prediction(update, context):
    user_id = update.message.chat_id

    if user_state.get(user_id) == "UNLOCKED":
        prediction = random.choice(predictions)
        update.message.reply_text(prediction)
    else:
        update.message.reply_text("⚠️ Tu n’as pas encore débloqué l’accès. Invite 3 amis pour activer les prédictions.")


# === MAIN ===
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_args=True))
    dp.add_handler(CommandHandler("prediction", prediction))  # nouvelle commande
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    print("✅ Bot démarré avec commande /prediction et plusieurs prédictions...")
    updater.idle()


if __name__ == "__main__":
    main()
